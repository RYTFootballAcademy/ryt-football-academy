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

## Sprint 4 – Sponsorship & Funding

### 22. Sponsors
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| name       | TEXT       | Sponsor name                 |
| industry   | TEXT       | Sector                       |
| email      | TEXT       | Contact email                |
| phone      | TEXT       | Contact phone                |
| website    | TEXT       | Sponsor website              |
| status     | TEXT       | Active / Inactive            |

---

### 23. Sponsor Contacts
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| sponsor_id | INTEGER FK | Linked to Sponsors           |
| name       | TEXT       | Contact person               |
| role       | TEXT       | Position                     |
| email      | TEXT       | Contact email                |
| phone      | TEXT       | Contact phone                |

---

### 24. Sponsorship Packages
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| sponsor_id | INTEGER FK | Linked to Sponsors           |
| name       | TEXT       | Package name                 |
| description| TEXT       | Package details              |
| value      | INTEGER    | Monetary value               |

---

### 25. Sponsorship Agreements
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| sponsor_id | INTEGER FK | Linked to Sponsors           |
| package_id | INTEGER FK | Linked to Sponsorship Packages |
| start_date | DATE       | Agreement start              |
| end_date   | DATE       | Agreement end                |
| status     | TEXT       | Active / Expired             |

---

### 26. Meetings
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| sponsor_id | INTEGER FK | Linked to Sponsors           |
| date       | DATE       | Meeting date                 |
| notes      | TEXT       | Meeting notes                |

---

### 27. Proposal Documents
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| sponsor_id | INTEGER FK | Linked to Sponsors           |
| title      | TEXT       | Proposal title               |
| content    | TEXT       | Proposal content             |
| status     | TEXT       | Draft / Submitted / Approved / Rejected |

---

### 28. Follow-ups
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| proposal_id| INTEGER FK | Linked to Proposal Documents |
| date       | DATE       | Follow-up date               |
| notes      | TEXT       | Follow-up notes              |

---

### 29. Funding Opportunities
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| name       | TEXT       | Funding opportunity name     |
| description| TEXT       | Details                      |
| deadline   | DATE       | Application deadline         |
| status     | TEXT       | Open / Closed                |

---

### 30. Grant Applications
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| funding_id | INTEGER FK | Linked to Funding Opportunities |
| player_id  | INTEGER FK | Linked to Players (if applicable) |
| date       | DATE       | Application date             |
| status     | TEXT       | Submitted / Approved / Rejected |
| notes      | TEXT       | Application notes            |

---

### 31. Supporting Documents
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| application_id | INTEGER FK | Linked to Grant Applications |
| file_path  | TEXT       | Document location            |
| description| TEXT       | Notes                        |

---

### 32. Outcomes
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| application_id | INTEGER FK | Linked to Grant Applications |
| decision   | TEXT       | Approved / Rejected          |
| date       | DATE       | Decision date                |
| notes      | TEXT       | Outcome notes                |

## Sprint 5 – Governance

### 33. Directors
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| first_name | TEXT       |                              |
| last_name  | TEXT       |                              |
| role       | TEXT       | Chairperson / Treasurer etc. |
| email      | TEXT       |                              |
| phone      | TEXT       |                              |
| status     | TEXT       | Active / Former              |

---

### 34. Members
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| first_name | TEXT       |                              |
| last_name  | TEXT       |                              |
| email      | TEXT       |                              |
| phone      | TEXT       |                              |
| membership_type | TEXT  | Ordinary / Honorary          |

---

### 35. Meetings
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| date       | DATE       | Meeting date                 |
| type       | TEXT       | Board / AGM / Special        |
| notes      | TEXT       | Meeting notes                |

---

### 36. Resolutions
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| meeting_id | INTEGER FK | Linked to Meetings           |
| title      | TEXT       | Resolution title             |
| content    | TEXT       | Resolution details           |
| status     | TEXT       | Passed / Rejected            |

---

### 37. Policies
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| title      | TEXT       | Policy title                 |
| content    | TEXT       | Policy content               |
| version    | TEXT       | Version number               |
| status     | TEXT       | Active / Archived            |

---

### 38. Compliance Tasks
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| title      | TEXT       | Task title                   |
| description| TEXT       | Task details                 |
| due_date   | DATE       | Deadline                     |
| status     | TEXT       | Pending / Completed          |

---

### 39. Annual Returns
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| year       | INTEGER    | Return year                  |
| date_filed | DATE       | Filing date                  |
| status     | TEXT       | Filed / Pending              |

---

### 40. Constitution Versions
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| version    | TEXT       | Version number               |
| date       | DATE       | Adoption date                |
| content    | TEXT       | Constitution text            |

## Sprint 6 – Commercial

### 41. Products
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| name       | TEXT       | Product name                 |
| category_id| INTEGER FK | Linked to Categories         |
| price      | INTEGER    | Unit price                   |
| stock      | INTEGER    | Quantity available           |
| status     | TEXT       | Active / Discontinued        |

---

### 42. Categories
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| name       | TEXT       | Category name                |
| description| TEXT       | Optional                     |

---

### 43. Orders
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| customer_id| INTEGER FK | Linked to Customers          |
| date       | DATE       | Order date                   |
| status     | TEXT       | Pending / Completed / Cancelled |
| total      | INTEGER    | Order total                  |

---

### 44. Order Items
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| order_id   | INTEGER FK | Linked to Orders             |
| product_id | INTEGER FK | Linked to Products           |
| quantity   | INTEGER    | Ordered quantity             |
| price      | INTEGER    | Unit price                   |

---

### 45. Customers
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| first_name | TEXT       |                              |
| last_name  | TEXT       |                              |
| email      | TEXT       |                              |
| phone      | TEXT       |                              |
| address    | TEXT       |                              |

---

### 46. Payments
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| order_id   | INTEGER FK | Linked to Orders             |
| amount     | INTEGER    | Payment amount               |
| date       | DATE       | Payment date                 |
| method     | TEXT       | Cash / EFT / Card            |
| reference  | TEXT       | Transaction reference        |

---

### 47. Camps
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| organization_id | INTEGER FK | Linked to Organization |
| name       | TEXT       | Camp name                    |
| location   | TEXT       | Camp venue                   |
| start_date | DATE       | Start date                   |
| end_date   | DATE       | End date                     |

---

### 48. Registrations
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| camp_id    | INTEGER FK | Linked to Camps              |
| player_id  | INTEGER FK | Linked to Players            |
| date       | DATE       | Registration date            |
| status     | TEXT       | Pending / Confirmed / Cancelled |

---

### 49. Camp Payments
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| registration_id | INTEGER FK | Linked to Registrations |
| amount     | INTEGER    | Payment amount               |
| date       | DATE       | Payment date                 |
| method     | TEXT       | Cash / EFT / Card            |

---

### 50. Camp Attendance
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | INTEGER PK | Primary key                  |
| camp_id    | INTEGER FK | Linked to Camps              |
| player_id  | INTEGER FK | Linked to Players            |
| date       | DATE       | Attendance date              |
| status     | TEXT       | Present / Absent             |
## Phase H - AI Layer 
### AI Conversations 
- id INTEGER PK 
- player_id INTEGER FK (Players.id) 
- sponsor_id INTEGER FK (Sponsors.id) 
- conversation_date DATE 
- input_text TEXT 
- output_text TEXT 
- context TEXT 
- status TEXT 
### Generated Proposals 
- id INTEGER PK 
- sponsor_id INTEGER FK 
- proposal_date DATE 
- title TEXT 
- content TEXT 
- generated_by TEXT 
- status TEXT 
### Generated Reports 
- id INTEGER PK 
- player_id INTEGER FK 
- report_date DATE 
- report_type TEXT 
- content TEXT 
- generated_by TEXT 
- status TEXT 
### Sponsor Recommendations 
- id INTEGER PK 
- sponsor_id INTEGER FK 
- recommendation_date DATE 
- recommendation_type TEXT 
- details TEXT 
- confidence_score REAL 
- status TEXT 
### Funding Recommendations 
- id INTEGER PK 
- funding_opportunity_id INTEGER FK 
- recommendation_date DATE 
- details TEXT 
- confidence_score REAL 
- status TEXT 
### Player Insights 
- id INTEGER PK 
- player_id INTEGER FK 
- insight_date DATE 
- insight_type TEXT 
- details TEXT 
- confidence_score REAL 
- status TEXT 
