# ai_agent/modules/npo_compliance.py
from typing import List, Dict

class NPOComplianceTracker:
    def __init__(self):
        self.directors: List[Dict] = []
        self.members: List[Dict] = []
        self.meetings: List[Dict] = []
        self.tasks: List[Dict] = []

    def add_director(self, name: str, active: bool = True):
        director = {"name": name, "active": active}
        self.directors.append(director)
        return director

    def add_member(self, name: str):
        member = {"name": name}
        self.members.append(member)
        return member

    def record_meeting(self, date: str, attendees: List[str]):
        meeting = {"date": date, "attendees": attendees}
        self.meetings.append(meeting)
        return meeting

    def mark_inactive_director(self, name: str):
        for d in self.directors:
            if d["name"] == name:
                d["active"] = False
                return d
        return None

    def add_task(self, task: str, due_date: str):
        compliance_task = {"task": task, "due_date": due_date, "completed": False}
        self.tasks.append(compliance_task)
        return compliance_task

    def complete_task(self, task: str):
        for t in self.tasks:
            if t["task"] == task:
                t["completed"] = True
                return t
        return None

    def list_tasks(self):
        return self.tasks
