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

## Sprint 2 – Football Operations

### 6. Attendance
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| player_id  | INTEGER FK | Linked to Players            |
| date       | DATE       | Training/match date          |
| status     | TEXT       | Present / Absent / Late      |

---

### 7. Training Sessions
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| team_id       | INTEGER FK | Linked to Teams              |
| coach_id      | INTEGER FK | Linked to Coaches            |
| date          | DATE       | Session date                 |
| time          | TEXT       | Session time                 |
| venue         | TEXT       | Training ground              |
| focus_area    | TEXT       | e.g. Passing, Fitness        |
| notes         | TEXT       | Session notes                |

---

### 8. Matches
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| team_id       | INTEGER FK | Linked to Teams              |
| opponent      | TEXT       | Opponent team name           |
| date          | DATE       | Match date                   |
| venue         | TEXT       | Stadium/field                |
| competition   | TEXT       | League / Cup / Friendly      |
| result        | TEXT       | Win / Loss / Draw            |

---

### 9. Match Events
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| match_id      | INTEGER FK | Linked to Matches            |
| player_id     | INTEGER FK | Linked to Players            |
| event_type    | TEXT       | Goal, Assist, Card, Substitution |
| minute        | INTEGER    | Minute of event              |
| notes         | TEXT       | Extra details                |

---

### 10. Player Statistics
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| player_id     | INTEGER FK | Linked to Players            |
| season        | TEXT       | Season identifier            |
| matches_played| INTEGER    |                              |
| goals         | INTEGER    |                              |
| assists       | INTEGER    |                              |
| yellow_cards  | INTEGER    |                              |
| red_cards     | INTEGER    |                              |
| minutes_played| INTEGER    |                              |

---

### 11. Development Reports
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| player_id     | INTEGER FK | Linked to Players            |
| coach_id      | INTEGER FK | Linked to Coaches            |
| date          | DATE       | Report date                  |
| strengths     | TEXT       | Player strengths             |
| weaknesses    | TEXT       | Areas to improve             |
| recommendations| TEXT      | Next steps                   |

---

### 12. Trials
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| player_id     | INTEGER FK | Linked to Players            |
| date          | DATE       | Trial date                   |
| result        | TEXT       | Passed / Failed              |
| notes         | TEXT       | Trial notes                  |

---

### 13. Injuries
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| player_id     | INTEGER FK | Linked to Players            |
| injury_type   | TEXT       | e.g. Hamstring, Ankle        |
| date          | DATE       | Injury date                  |
| recovery_date | DATE       | Expected recovery            |
| status        | TEXT       | Active / Recovered           |

---

### 14. Fitness Tests
| Column        | Type       | Notes                        |
|---------------|------------|------------------------------|
| id            | INTEGER PK | Primary key                  |
| player_id     | INTEGER FK | Linked to Players            |
| date          | DATE       | Test date                    |
| test_type     | TEXT       | e.g. Sprint, Endurance       |
| result        | TEXT       | Recorded result              |
| notes         | TEXT       | Extra details                |

## Sprint 3 – Finance

### 15. Fee Categories
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| name       | TEXT       | e.g. Registration, Monthly   |
| description| TEXT       | Optional                     |

---

### 16. Player Fees
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| player_id  | INTEGER FK | Linked to Players            |
| category_id| INTEGER FK | Linked to Fee Categories     |
| amount     | INTEGER    | Fee amount                   |
| due_date   | DATE       | Payment due date             |
| status     | TEXT       | Pending / Paid / Overdue     |

---

### 17. Payments
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| player_id  | INTEGER FK | Linked to Players            |
| fee_id     | INTEGER FK | Linked to Player Fees        |
| amount     | INTEGER    | Amount paid                  |
| date       | DATE       | Payment date                 |
| method     | TEXT       | Cash / EFT / Card            |
| reference  | TEXT       | Transaction reference        |

---

### 18. Expenses
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| description| TEXT       | Expense details              |
| amount     | INTEGER    | Expense amount               |
| date       | DATE       | Expense date                 |
| category   | TEXT       | e.g. Equipment, Travel       |

---

### 19. Income
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| source     | TEXT       | e.g. Sponsorship, Donation   |
| amount     | INTEGER    | Income amount                |
| date       | DATE       | Income date                  |

---

### 20. Budgets
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| year       | INTEGER    | Budget year                  |
| total      | INTEGER    | Planned budget               |
| notes      | TEXT       | Optional                     |

---

### 21. Bank Accounts
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| bank_name  | TEXT       | Bank name                    |
| account_number | TEXT   | Account number               |
| account_type | TEXT     | Savings / Current            |
| status     | TEXT       | Active / Closed              |
