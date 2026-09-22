"""Browser-assisted BizPortal workflow runner.

This runner intentionally leaves identity verification, factual legal
declarations, OTPs and card payment to the user. It automates navigation and
recordkeeping around those checkpoints.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Iterable

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from ai_agent.faos.company_models import (
    ExternalPortalWorkflow,
    ExternalPortalWorkflowEvent,
)
from ai_agent.modules.database import SessionLocal, init_db


BIZPORTAL_LOGIN = "https://www.bizportal.gov.za/login.aspx"
BIZPORTAL_SERVICES = "https://www.bizportal.gov.za/services.aspx"
BIZPORTAL_BIZPROFILE = "https://www.bizportal.gov.za/bizprofile.aspx"

SERVICE_LABELS = {
    "cipc_reinstatement": ("Reinstatement", "Re-instatement"),
    "cipc_annual_return": ("Annual Return Filing", "Annual Returns", "Annual Return"),
    "cipc_beneficial_ownership": ("Beneficial Ownership",),
    "cipc_director_change": ("Director Changes", "Director Amendments", "Directors"),
    "information_regulator": ("Information Regulator Services", "Information Regulator"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(db, workflow, event_type: str, message: str, page_url: str | None = None) -> None:
    db.add(
        ExternalPortalWorkflowEvent(
            workflow_id=workflow.id,
            event_time=utc_now(),
            event_type=event_type,
            message=message,
            page_url=page_url,
        )
    )
    workflow.updated_at = utc_now()
    if page_url:
        workflow.last_url = page_url
    db.commit()


def _set_state(db, workflow, status: str, step: str, page_url: str | None = None) -> None:
    workflow.status = status
    workflow.current_step = step
    workflow.updated_at = utc_now()
    if page_url:
        workflow.last_url = page_url
    db.commit()


def _navigate(page: Page, url: str, *, label: str) -> bool:
    """Navigate without treating a slow government page as a fatal error.

    BizPortal can take well over 30 seconds to finish DOMContentLoaded. We wait
    for the navigation to commit, then give the DOM a shorter best-effort wait.
    If even the commit times out, keep the visible browser open so the user can
    finish the navigation manually rather than losing the whole workflow.
    """
    try:
        page.goto(url, wait_until="commit", timeout=90000)
    except PlaywrightTimeoutError:
        print()
        print(f"{label} is taking unusually long to respond.")
        print("The browser will remain open. If the page is usable there, continue in it.")
        return False

    try:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
    except PlaywrightTimeoutError:
        # The ASP.NET page may continue loading scripts/resources while already
        # being interactive enough for the user or the next automation step.
        pass
    return True


def _click_first_text(page: Page, labels: Iterable[str]) -> bool:
    for label in labels:
        pattern = re.compile(re.escape(label), re.IGNORECASE)
        candidates = [
            page.get_by_role("link", name=pattern),
            page.get_by_role("button", name=pattern),
            page.get_by_text(pattern),
        ]
        for candidate in candidates:
            try:
                if candidate.count() and candidate.first.is_visible():
                    candidate.first.click()
                    page.wait_for_load_state("domcontentloaded")
                    return True
            except Exception:
                continue
    return False


def _fill_registration_number(page: Page, registration_number: str) -> bool:
    labels = (
        "Enterprise Number",
        "Registration Number",
        "Company Number",
        "Enterprise No",
        "Enterprise",
        "Company",
    )
    for label in labels:
        try:
            field = page.get_by_label(re.compile(label, re.IGNORECASE))
            if field.count() and field.first.is_visible():
                field.first.fill(registration_number)
                return True
        except Exception:
            continue

    selectors = (
        "input[placeholder*='Enterprise' i]",
        "input[placeholder*='Registration' i]",
        "input[placeholder*='Company' i]",
        "input[name*='enterprise' i]",
        "input[id*='enterprise' i]",
        "input[name*='registration' i]",
        "input[id*='registration' i]",
        "input[name*='company' i]",
        "input[id*='company' i]",
    )
    for selector in selectors:
        try:
            field = page.locator(selector)
            if field.count() and field.first.is_visible():
                field.first.fill(registration_number)
                return True
        except Exception:
            continue

    try:
        fields = page.locator("input[type='text']:visible")
        for index in range(fields.count()):
            field = fields.nth(index)
            surrounding = ""
            try:
                surrounding = field.evaluate(
                    """el => [
                        el.getAttribute('placeholder') || '',
                        el.getAttribute('name') || '',
                        el.getAttribute('id') || '',
                        el.parentElement ? el.parentElement.innerText : ''
                    ].join(' ')"""
                )
            except Exception:
                pass
            if re.search(r"enterprise|registration|company", surrounding, re.IGNORECASE):
                field.fill(registration_number)
                return True
        if fields.count() == 1:
            fields.first.fill(registration_number)
            return True
    except Exception:
        pass
    return False


def _extract_reference(text: str) -> str | None:
    patterns = (
        r"(?:reference|tracking|transaction)s*(?:number|no.?|#)?s*[:-]s*([A-Z0-9-/]+)",
        r"(CIPC[-/A-Z0-9]{5,})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def run_workflow(workflow_id: int) -> int:
    # Standalone scripts do not pass through FastAPI lifespan startup. Load every
    # mapped FAOS model and apply additive schema creation before opening the
    # session so cross-model foreign keys (for example organizations.id) resolve.
    init_db()
    db = SessionLocal()
    workflow = db.get(ExternalPortalWorkflow, workflow_id)
    if workflow is None:
        print(f"FAOS portal workflow {workflow_id} was not found.")
        db.close()
        return 2

    labels = SERVICE_LABELS.get(workflow.workflow_type)
    if not labels:
        workflow.status = "Failed"
        workflow.current_step = "Unsupported workflow"
        workflow.notes = f"Unsupported workflow type: {workflow.workflow_type}"
        db.commit()
        db.close()
        return 2

    workflow.started_at = utc_now()
    workflow.status = "Running"
    workflow.current_step = "Launching browser"
    db.commit()

    print()
    print("FAOS BizPortal Assistant")
    print("========================")
    print(f"Workflow: {workflow.workflow_type}")
    print(f"Enterprise: {workflow.registration_number or 'not set'}")
    print()
    print("Security boundary:")
    print("- Enter CIPC password, OTP/security answers and card details only in the browser.")
    print("- FAOS does not store those values.")
    print("- The assistant will stop before a final legal submission.")
    print()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            login_loaded = _navigate(page, BIZPORTAL_LOGIN, label="BizPortal login")
            if not login_loaded:
                _set_state(
                    db,
                    workflow,
                    "Waiting for User",
                    "Open BizPortal login manually",
                    page.url,
                )
                _event(
                    db,
                    workflow,
                    "navigation_slow",
                    "Automatic navigation to BizPortal login timed out; visible-browser fallback activated.",
                    page.url,
                )
                print()
                print("If the BizPortal login page did not appear, open it in the visible browser:")
                print(BIZPORTAL_LOGIN)
            _set_state(db, workflow, "Waiting for User", "CIPC login", page.url)
            _event(
                db,
                workflow,
                "login_required",
                "Visible BizPortal browser opened. User must complete login directly.",
                page.url,
            )

            input(
                "Complete the BizPortal login in the browser. "
                "When you are logged in, return here and press ENTER..."
            )

            if workflow.workflow_type == "cipc_reinstatement":
                _set_state(db, workflow, "Running", "Opening BizProfile", page.url)
                profile_loaded = _navigate(
                    page,
                    BIZPORTAL_BIZPROFILE,
                    label="BizProfile",
                )
                if not profile_loaded:
                    _set_state(
                        db,
                        workflow,
                        "Waiting for User",
                        "Open BizProfile manually",
                        page.url,
                    )
                    print()
                    print("Open BizProfile in the visible browser:")
                    print(BIZPORTAL_BIZPROFILE)
                    input("Press ENTER when BizProfile is open...")

                if workflow.registration_number:
                    filled = _fill_registration_number(page, workflow.registration_number)
                    if filled:
                        _event(
                            db,
                            workflow,
                            "registration_number_filled",
                            "Enterprise registration number was entered in BizProfile by FAOS.",
                            page.url,
                        )
                        _click_first_text(
                            page,
                            ("Search", "Continue", "View", "Lookup", "Proceed"),
                        )
                        try:
                            page.wait_for_timeout(1500)
                        except Exception:
                            pass
                    else:
                        _set_state(
                            db,
                            workflow,
                            "Waiting for User",
                            "Enter enterprise number in BizProfile",
                            page.url,
                        )
                        print(
                            "FAOS could not safely identify the BizProfile enterprise field. "
                            "Enter the enterprise number in the visible browser."
                        )
                        input("Press ENTER after the enterprise profile is displayed...")

                clicked = _click_first_text(
                    page,
                    (
                        "Apply for Reinstatement",
                        "Apply for Re-instatement",
                        "Reinstatement",
                        "Re-instatement",
                        "Reinstate",
                    ),
                )
                if not clicked:
                    _set_state(
                        db,
                        workflow,
                        "Waiting for User",
                        "Open reinstatement action from BizProfile",
                        page.url,
                    )
                    print()
                    print(
                        "FAOS found BizProfile but could not safely identify the "
                        "reinstatement action."
                    )
                    print(
                        "If the enterprise profile is displayed, use only the "
                        "Reinstatement/Re-instatement action for this workflow. "
                        "Do not file annual returns or director changes yet."
                    )
                    input("Press ENTER only when the reinstatement application page is open...")
                else:
                    _event(
                        db,
                        workflow,
                        "service_opened",
                        "Opened the reinstatement action from BizProfile.",
                        page.url,
                    )
            else:
                _set_state(db, workflow, "Running", "Opening BizPortal services", page.url)
                services_loaded = _navigate(
                    page,
                    BIZPORTAL_SERVICES,
                    label="BizPortal services page",
                )
                if not services_loaded:
                    _set_state(
                        db,
                        workflow,
                        "Waiting for User",
                        "Open BizPortal services manually",
                        page.url,
                    )
                    _event(
                        db,
                        workflow,
                        "navigation_slow",
                        "Automatic navigation to BizPortal services timed out; visible-browser fallback activated.",
                        page.url,
                    )
                    print()
                    print("Open the BizPortal services page in the visible browser if needed:")
                    print(BIZPORTAL_SERVICES)
                    input("Press ENTER when the services page is open...")

                clicked = _click_first_text(page, labels)
                if not clicked:
                    _set_state(
                        db,
                        workflow,
                        "Waiting for User",
                        "Navigate to requested service",
                        page.url,
                    )
                    print()
                    print(
                        "FAOS could not safely identify the requested service on this "
                        "version of BizPortal."
                    )
                    input("Press ENTER when the correct service page is open...")
                else:
                    _event(
                        db,
                        workflow,
                        "service_opened",
                        f"Opened BizPortal service matching: {', '.join(labels)}",
                        page.url,
                    )

                if workflow.registration_number:
                    filled = _fill_registration_number(page, workflow.registration_number)
                    if filled:
                        _event(
                            db,
                            workflow,
                            "registration_number_filled",
                            "Enterprise registration number was entered by FAOS.",
                            page.url,
                        )
                        _click_first_text(page, ("Search", "Continue", "Next", "Proceed"))
                    else:
                        _set_state(
                            db,
                            workflow,
                            "Waiting for User",
                            "Enter enterprise number",
                            page.url,
                        )
                        print(
                            "FAOS could not safely identify the enterprise-number field. "
                            "Enter it in the browser yourself."
                        )
                        input("Press ENTER after the enterprise is selected...")

            if workflow.workflow_type == "cipc_reinstatement":
                _set_state(
                    db,
                    workflow,
                    "Waiting for User",
                    "Eligibility declaration and application review",
                    page.url,
                )
                print()
                print(
                    "Review the reinstatement application in the browser. "
                    "Any declaration about whether the company was operating or had "
                    "economic value must be answered by you based on the facts."
                )
                print(
                    "Complete any required factual declarations, but DO NOT click "
                    "the final Submit/Apply button yet."
                )
                input("Press ENTER once the application is complete and ready to submit...")

            _set_state(
                db,
                workflow,
                "Awaiting Approval",
                "Final external submission approval",
                page.url,
            )
            _event(
                db,
                workflow,
                "approval_required",
                "Portal application prepared. Explicit Founder approval required before submission.",
                page.url,
            )

            print()
            print("FINAL EXTERNAL ACTION CHECKPOINT")
            print("No application has been intentionally submitted by FAOS at this checkpoint.")
            approval = input(
                "Type APPROVE SUBMISSION exactly to allow FAOS to click the portal "
                "submit/apply button, or press ENTER to stop: "
            ).strip()

            if approval != "APPROVE SUBMISSION":
                workflow.status = "Paused"
                workflow.current_step = "Awaiting future submission approval"
                workflow.updated_at = utc_now()
                db.commit()
                _event(
                    db,
                    workflow,
                    "paused",
                    "User did not approve external submission.",
                    page.url,
                )
                print("Workflow paused. Nothing further was submitted by FAOS.")
                browser.close()
                db.close()
                return 0

            submitted = _click_first_text(
                page,
                ("Submit", "Apply", "Confirm Application", "Submit Application"),
            )
            if not submitted:
                _set_state(
                    db,
                    workflow,
                    "Waiting for User",
                    "Manual final submission",
                    page.url,
                )
                print()
                print(
                    "FAOS could not safely identify the final submit button. "
                    "If the page is correct, click the final submit button yourself."
                )
                input("Press ENTER after the application has been submitted...")

            _event(
                db,
                workflow,
                "submitted",
                "External submission step completed after explicit user approval.",
                page.url,
            )

            if workflow.workflow_type == "cipc_reinstatement":
                _set_state(
                    db,
                    workflow,
                    "Waiting for User",
                    "CIPC card payment",
                    page.url,
                )
                print()
                print(
                    "Complete any CIPC card payment, OTP or banking authentication "
                    "directly in the browser. FAOS will not enter or store payment data."
                )
                input("Press ENTER after payment/confirmation is complete...")

            page.wait_for_timeout(1200)
            body_text = ""
            try:
                body_text = page.locator("body").inner_text(timeout=5000)
            except Exception:
                pass

            reference = _extract_reference(body_text)
            workflow.external_reference = reference
            workflow.last_url = page.url
            workflow.status = (
                "Submitted - Awaiting CIPC Processing"
                if workflow.service == "BizPortal / CIPC"
                else "Submitted"
            )
            workflow.current_step = "Await regulator outcome"
            workflow.updated_at = utc_now()
            db.commit()
            _event(
                db,
                workflow,
                "workflow_submitted",
                (
                    f"Submission recorded with reference {reference}."
                    if reference
                    else "Submission recorded; no reference was automatically detected."
                ),
                page.url,
            )

            print()
            print("FAOS recorded the submission workflow.")
            if reference:
                print(f"Reference detected: {reference}")
            else:
                print(
                    "No reference was detected automatically. You can record it later "
                    "from the company dashboard."
                )
            input("Press ENTER to close the controlled browser...")
            browser.close()

    except Exception as exc:
        workflow = db.get(ExternalPortalWorkflow, workflow_id)
        if workflow is not None:
            workflow.status = "Failed"
            workflow.current_step = "Browser automation error"
            workflow.updated_at = utc_now()
            workflow.notes = (
                ((workflow.notes or "") + " ").strip()
                + f"Automation error: {type(exc).__name__}: {exc}"
            ).strip()
            db.commit()
            _event(
                db,
                workflow,
                "error",
                f"{type(exc).__name__}: {exc}",
                workflow.last_url,
            )
        print(f"Portal automation failed: {type(exc).__name__}: {exc}")
        db.close()
        return 1

    db.close()
    return 0
