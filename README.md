# Health and Fitness Club Management System

A comprehensive database-driven fitness club management system with member registration, trainer scheduling, class management, and administrative functions.

## LINK TO YOUTUBE: [https://www.youtube.com/watch?v=JdUe-LjPliE]

## Technology Stack

- **Database:** PostgreSQL 14+
- **Application:** Python 3.8+
- **Database Driver:** psycopg2
- **Interface:** Command-Line Interface (CLI)

### Entities Implemented (6)

- Member
- Trainer
- AdminStaff
- Room
- Equipment
- FitnessGoal
- HealthMetric
- TrainerAvailability
- Class
- PersonalTrainingSession
- ClassRegistration
- Bill
- Payment

### Relationships Implemented (5)

- Member → FitnessGoal (1:N)
- Member → HealthMetric (1:N)
- Trainer → TrainerAvailability (1:N)
- Trainer → PersonalTrainingSession (1:N)
- Member → PersonalTrainingSession (N:1)
- Member → ClassRegistration (1:N)
- Class → ClassRegistration (1:N)
- Member → Bill (1:N)
- Bill → Payment (1:N)
- Room → Equipment (1:N)

### Operations Implemented (8)

**Member Functions (4 operations)**

- User Registration - Create new member account with validation
- Profile Management - Update personal info, manage fitness goals, add health metrics
- Member Dashboard - Comprehensive view using database VIEW
- Schedule Personal Training - Book sessions with availability and conflict checking

**Trainer Functions (2 operations)**

- Set Availability - Define working hours with overlap prevention
- View Schedule - See assigned sessions, classes, and availability

**Admin Functions (2 operations)**

- Room Booking Management - View and manage room schedules
- Equipment Maintenance - Track equipment status and maintenance

### Advanced SQL Features

- **View:** MemberDashboard - Aggregates member data for quick access
- **Trigger 1:** class_enrollment_trigger - Auto-updates class enrollment counts
- **Trigger 2:** payment_bill_update_trigger - Auto-updates bill payment status
- **Indexes:** Created on frequently queried columns for performance

## Database Schema

### Core Tables

- **Member:** User accounts with personal information
- **Trainer:** Trainer profiles and specializations
- **AdminStaff:** Administrative user accounts
- **Room:** Physical spaces for activities
- **Equipment:** Gym equipment with maintenance tracking
- **FitnessGoal:** Member fitness objectives
- **HealthMetric:** Historical health data tracking
- **TrainerAvailability:** Trainer working schedules
- **Class:** Group fitness classes
- **PersonalTrainingSession:** One-on-one training appointments
- **ClassRegistration:** Member class enrollments
- **Bill:** Financial invoices
- **Payment:** Payment transactions

## Installation & Setup

### Prerequisites

- PostgreSQL 14 or higher installed
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install psycopg2-binary
```

### Step 2: Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fitness_club;

# Exit psql
\q
```

### Step 3: Initialize Database Schema
```bash
# Run DDL script
psql -U postgres -d fitness_club -f sql/DDL.sql

# Load sample data
psql -U postgres -d fitness_club -f sql/DML.sql
```

### Step 4: Configure Database Connection

Edit `app/app.py` and update the database connection parameters:
```python
self.connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn,
    maxconn,
    host="localhost",
    database="fitness_club",
    user="postgres",
    password="your_password",  # Change this!
    port="5432"
)
```

### Step 5: Run Application
```bash
cd app
python app.py
```

## Sample Login Credentials

### Members

- Email: `john.doe@email.com`, Password: `pass123`
- Email: `jane.smith@email.com`, Password: `pass456`

### Trainers

- Email: `alex.trainer@fitness.com`, Password: `trainer123`
- Email: `lisa.coach@fitness.com`, Password: `trainer456`

### Admin

- Email: `admin@fitness.com`, Password: `admin123`

## Features Demonstration

### Member Features

- **Registration:** New users can sign up with email validation
- **Dashboard:** View health metrics, goals, upcoming sessions, and billing
- **Health Tracking:** Log weight, heart rate, blood pressure (historical data)
- **Fitness Goals:** Set and track goals with progress monitoring
- **Session Booking:** Schedule PT sessions with conflict checking
- **Class Registration:** Enroll in group classes with capacity limits

### Trainer Features

- **Availability Management:** Set weekly schedules with overlap prevention
- **Schedule View:** See all assigned sessions and classes
- **Member Lookup:** Search and view client information (read-only)

### Admin Features

- **Room Management:** View schedules and prevent double-booking
- **Equipment Tracking:** Monitor status and log maintenance
- **Billing System:** Generate bills and record payments

## Business Rules Enforced

### Data Integrity

- Unique email addresses for all users
- Valid email format (regex check)
- Date of birth must be valid date
- Time ranges validated (start < end)
- Positive values for capacity, amounts

### Scheduling Constraints

- Trainer availability checked before booking
- No overlapping sessions for same trainer
- Room capacity enforced for classes
- No double-booking of rooms
- Historical health metrics (no overwrites)

### Financial Rules

- Bills automatically marked as "Paid" when full amount received
- Payment amounts validated
- Transaction references tracked

## Database Normalization

All tables are normalized to at least 3NF (Third Normal Form):

- No repeating groups (1NF)
- All non-key attributes depend on entire primary key (2NF)
- No transitive dependencies (3NF)

## Project Structure
```
/project-root
├── /sql
│   ├── DDL.sql          # Database schema definition
│   └── DML.sql          # Sample data
├── /app
│   └── app.py           # Python application
├── /docs
│   └── ERD.pdf          # ER diagram and documentation
└── README.md            # This file
```

## Key Design Decisions

### Historical Data Tracking

- **HealthMetric:** Never overwrites - each entry is timestamped
- Members can track progress over time
- Dashboard shows latest metrics

### Trigger Implementation

- **Auto-enrollment:** Class enrollment count updates automatically
- **Payment processing:** Bill status updates when payments recorded
- Reduces application complexity and ensures consistency

### View for Performance

- **MemberDashboard:** Precomputed aggregations
- Faster dashboard loading
- Indexed for quick access

### Validation Layers

- Database constraints (CHECK, FOREIGN KEY)
- Application-level validation
- User-friendly error messages

## Testing Edge Cases

### Tested Scenarios

✓ Duplicate email registration (rejected)  
✓ Booking unavailable trainer (rejected)  
✓ Overlapping session booking (rejected)  
✓ Class at full capacity (rejected)  
✓ Trainer availability overlap (rejected)  
✓ Invalid date formats (handled)  
✓ Payment exceeding bill amount (warning)  
✓ Equipment status transitions  
✓ Historical metric tracking


## Troubleshooting

### Connection Error

- Verify PostgreSQL is running: `sudo service postgresql status`
- Check database name and credentials
- Ensure firewall allows port 5432

### Import Error (psycopg2)
```bash
pip install --upgrade psycopg2-binary
```

### Data Not Loading
```bash
# Re-run scripts in order
psql -U postgres -d fitness_club -f sql/DDL.sql
psql -U postgres -d fitness_club -f sql/DML.sql
```

## Contact & Support

For questions or issues, please contact:

- **Email:** [eyongsammy72@gmail.com]

## Acknowledgments

- PostgreSQL Documentation
- Python psycopg2 Documentation
- Course materials and lectures

---

**Project Completed:** November 2025  
**Database Course:** COMP 3005
