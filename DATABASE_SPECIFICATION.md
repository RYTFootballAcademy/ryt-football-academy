# FAOS Database Specification v1.0

This document defines the Football Academy Operating System (FAOS) database architecture.  
It is the single source of truth for all tables, fields, relationships, and migrations.

---

## Sprint 1 – Core Academy

### 1. Organizations
| Column              | Type     | Notes                          |
|---------------------|----------|--------------------------------|
| id                  | INTEGER PK | Primary key                  |
| name                | TEXT     | Academy name                  |
| registration_number | TEXT     | Optional                      |
| npo_number          | TEXT     | NPO registration              |
| established         | DATE     | Year founded                  |
| town                | TEXT     | Schweizer-Reneke              |
| province            | TEXT     | North West                    |
| country             | TEXT     | South Africa                  |
| email               | TEXT     | Official email                |
| phone               | TEXT     | Academy phone                 |
| website             | TEXT     | Public website                |
| status              | TEXT     | Active / Inactive             |

**Relationships:**  
Organization → Teams, Players, Sponsors, Directors, Camps

---

### 2. Teams
| Column         | Type     | Notes                  |
|----------------|----------|------------------------|
| id             | INTEGER PK | Primary key          |
| organization_id| INTEGER FK | Linked to Organization |
| name           | TEXT     | Team name             |
| age_group      | TEXT     | e.g. U13, U15         |
| season         | TEXT     | Current season        |
| coach_id       | INTEGER FK | Linked to Coaches   |
| training_days  | TEXT     | e.g. Mon/Wed/Fri      |
| training_time  | TEXT     | e.g. 16:00            |
| venue          | TEXT     | Training venue        |

**Relationships:**  
Team → Players, Training Sessions, Matches

---

### 3. Coaches
| Column             | Type     | Notes                        |
|--------------------|----------|------------------------------|
| id                 | INTEGER PK | Primary key                |
| organization_id    | INTEGER FK | Linked to Organization      |
| first_name         | TEXT     |                              |
| last_name          | TEXT     |                              |
| phone              | TEXT     |                              |
| email              | TEXT     |                              |
| qualifications     | TEXT     | Certificates, diplomas       |
| license_level      | TEXT     | CAF, SAFA, etc.              |
| employment_status  | TEXT     | Active / Former              |

---

### 4. Parents
| Column               | Type     | Notes                        |
|----------------------|----------|------------------------------|
| id                   | INTEGER PK | Primary key                |
| organization_id      | INTEGER FK | Linked to Organization      |
| first_name           | TEXT     |                              |
| last_name            | TEXT     |                              |
| phone                | TEXT     |                              |
| whatsapp             | TEXT     |                              |
| email                | TEXT     |                              |
| address              | TEXT     |                              |
| emergency_contact    | TEXT     |                              |
| relationship_to_player| TEXT    | Mother, Father, Guardian     |

**Relationships:**  
One Parent → Many Players

---

### 5. Players
| Column             | Type     | Notes                        |
|--------------------|----------|------------------------------|
| id                 | INTEGER PK | Primary key                |
| parent_id          | INTEGER FK | Linked to Parents           |
| team_id            | INTEGER FK | Linked to Teams             |
| first_name         | TEXT     |                              |
| last_name          | TEXT     |                              |
| preferred_name     | TEXT     | Nickname                     |
| gender             | TEXT     | Male/Female                  |
| DOB                | DATE     | Date of birth                |
| primary_position   | TEXT     | e.g. Striker                 |
| secondary_position | TEXT     | e.g. Midfielder              |
| preferred_foot     | TEXT     | Left/Right                   |
| registration_date  | DATE     | Academy registration         |
| status             | TEXT     | Active / Inactive            |
| squad_number       | INTEGER  | Jersey number                |
| allergies          | TEXT     | Medical info                 |
| injuries           | TEXT     | Medical info                 |
| medication         | TEXT     | Medical info                 |
| school             | TEXT     | Education                    |
| grade              | TEXT     | Education                    |
| profile_photo      | TEXT     | Path/URL                     |
| ID_number          | TEXT     | National ID                  |
| notes              | TEXT     | Admin notes                  |

**Relationships:**  
Parent → Players → Attendance, Fees, Trials, Evaluations, Messages, Reports
