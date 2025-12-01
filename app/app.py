"""
Health and Fitness Club Management System
Main Application File
"""

import psycopg2
from psycopg2 import pool
from datetime import datetime, date, time
import sys


class Database:
    """Database connection manager"""

    def __init__(self):
        self.connection_pool = None

    def initialize_pool(self, minconn=1, maxconn=10):
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn,
                maxconn,
                host="localhost",
                database="fitness_club",
                user="postgres",
                password="",  # Change this
                port="5432"
            )
            print("Database connection pool created successfully")
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            sys.exit(1)

    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()

    def return_connection(self, connection):
        """Return connection to pool"""
        self.connection_pool.putconn(connection)

    def close_all_connections(self):
        """Close all connections"""
        if self.connection_pool:
            self.connection_pool.closeall()


# Global database instance
db = Database()

# ============================================================================
# MEMBER FUNCTIONS (4 operations required)
# ============================================================================


def member_registration():
    """Member Function 1: User Registration"""
    print("\n=== Member Registration ===")

    email = input("Email: ").strip()
    password = input("Password: ").strip()
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    dob = input("Date of Birth (YYYY-MM-DD): ").strip()
    gender = input("Gender (Male/Female/Other): ").strip()
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT email FROM Member WHERE email = %s", (email,))
        if cursor.fetchone():
            print("❌ Error: Email already registered!")
            return

        # Insert new member
        cursor.execute("""
            INSERT INTO Member (email, password, first_name, last_name, date_of_birth, 
                               gender, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING member_id
        """, (email, password, first_name, last_name, dob, gender, phone, address))

        member_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✓ Registration successful! Member ID: {member_id}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def profile_management(member_id):
    """Member Function 2: Profile Management - Update details and manage goals"""
    print("\n=== Profile Management ===")
    print("1. Update Personal Information")
    print("2. Add/Update Fitness Goal")
    print("3. Add Health Metric")

    choice = input("\nSelect option: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        if choice == '1':
            # Update personal information
            print("\n--- Update Personal Information ---")
            print("Leave blank to keep current value")

            phone = input("New Phone: ").strip()
            address = input("New Address: ").strip()

            updates = []
            params = []

            if phone:
                updates.append("phone = %s")
                params.append(phone)
            if address:
                updates.append("address = %s")
                params.append(address)

            if updates:
                params.append(member_id)
                query = f"UPDATE Member SET {
                    ', '.join(updates)} WHERE member_id = %s"
                cursor.execute(query, params)
                conn.commit()
                print("✓ Profile updated successfully!")
            else:
                print("No changes made.")

        elif choice == '2':
            # Add or update fitness goal
            print("\n--- Fitness Goal Management ---")
            goal_type = input(
                "Goal Type (e.g., Weight Loss, Muscle Gain): ").strip()
            target = float(input("Target Value: "))
            current = float(input("Current Value: "))
            target_date = input("Target Date (YYYY-MM-DD): ").strip()

            cursor.execute("""
                INSERT INTO FitnessGoal (member_id, goal_type, target_value, 
                                        current_value, target_date, status)
                VALUES (%s, %s, %s, %s, %s, 'Active')
            """, (member_id, goal_type, target, current, target_date))

            conn.commit()
            print("✓ Fitness goal added successfully!")

        elif choice == '3':
            # Add health metric
            print("\n--- Add Health Metric ---")
            weight = input("Weight (lbs): ").strip()
            height = input("Height (inches): ").strip()
            heart_rate = input("Heart Rate (bpm): ").strip()
            blood_pressure = input("Blood Pressure (e.g., 120/80): ").strip()
            body_fat = input("Body Fat % (optional): ").strip()
            notes = input("Notes (optional): ").strip()

            cursor.execute("""
                INSERT INTO HealthMetric (member_id, weight, height, heart_rate, 
                                         blood_pressure, body_fat_percentage, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (member_id,
                  float(weight) if weight else None,
                  float(height) if height else None,
                  int(heart_rate) if heart_rate else None,
                  blood_pressure if blood_pressure else None,
                  float(body_fat) if body_fat else None,
                  notes if notes else None))

            conn.commit()
            print("✓ Health metric recorded successfully!")

        else:
            print("Invalid option")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def member_dashboard(member_id):
    """Member Function 3: Dashboard - View personalized summary"""
    print("\n=== Member Dashboard ===")

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Use the view we created
        cursor.execute("""
            SELECT first_name, last_name, email, latest_weight, latest_heart_rate,
                   last_metric_date, active_goals, upcoming_sessions, 
                   classes_attended, pending_balance
            FROM MemberDashboard
            WHERE member_id = %s
        """, (member_id,))

        row = cursor.fetchone()
        if row:
            print(f"\n👤 {row[0]} {row[1]} ({row[2]})")
            print("=" * 60)
            print("\n📊 LATEST HEALTH METRICS:")
            print(f"  Weight: {row[3] if row[3] else 'N/A'} lbs")
            print(f"  Heart Rate: {row[4] if row[4] else 'N/A'} bpm")
            print(f"  Last Updated: {row[5] if row[5] else 'Never'}")

            print("\n🎯 FITNESS GOALS:")
            print(f"  Active Goals: {row[6]}")

            # Show goal details
            cursor.execute("""
                SELECT goal_type, current_value, target_value, target_date
                FROM FitnessGoal
                WHERE member_id = %s AND status = 'Active'
            """, (member_id,))

            for goal in cursor.fetchall():
                progress = (goal[1] / goal[2] * 100) if goal[2] else 0
                print(f"  - {goal[0]}: {goal[1]
                                        }/{goal[2]} (Target: {goal[3]})")

            print("\n📅 SCHEDULE:")
            print(f"  Upcoming PT Sessions: {row[7]}")
            print(f"  Classes Attended: {row[8]}")

            # Show upcoming sessions
            cursor.execute("""
                SELECT session_date, start_time, end_time, 
                       t.first_name || ' ' || t.last_name as trainer_name,
                       r.room_name
                FROM PersonalTrainingSession pts
                JOIN Trainer t ON pts.trainer_id = t.trainer_id
                JOIN Room r ON pts.room_id = r.room_id
                WHERE pts.member_id = %s 
                  AND pts.session_date >= CURRENT_DATE 
                  AND pts.status = 'Scheduled'
                ORDER BY session_date, start_time
                LIMIT 3
            """, (member_id,))

            sessions = cursor.fetchall()
            if sessions:
                print("\n  Next Sessions:")
                for s in sessions:
                    print(f"    • {s[0]} at {s[1]} with {s[3]} ({s[4]})")

            print("\n💰 BILLING:")
            print(f"  Pending Balance: ${row[9]:.2f}")
        else:
            print("Member not found")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def schedule_personal_training(member_id):
    """Member Function 4: Schedule Personal Training Session"""
    print("\n=== Schedule Personal Training Session ===")

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Show available trainers
        cursor.execute("""
            SELECT trainer_id, first_name, last_name, specialization
            FROM Trainer
            ORDER BY trainer_id
        """)

        trainers = cursor.fetchall()
        print("\nAvailable Trainers:")
        for t in trainers:
            print(f"  {t[0]}. {t[1]} {t[2]} - {t[3]}")

        trainer_id = int(input("\nSelect Trainer ID: "))
        session_date = input("Session Date (YYYY-MM-DD): ").strip()
        start_time = input("Start Time (HH:MM): ").strip()
        end_time = input("End Time (HH:MM): ").strip()

        # Check trainer availability
        day_of_week = datetime.strptime(
            session_date, '%Y-%m-%d').strftime('%A')

        cursor.execute("""
            SELECT availability_id
            FROM TrainerAvailability
            WHERE trainer_id = %s 
              AND day_of_week = %s
              AND start_time <= %s
              AND end_time >= %s
        """, (trainer_id, day_of_week, start_time, end_time))

        if not cursor.fetchone():
            print("❌ Error: Trainer not available at this time!")
            return

        # Check for trainer conflicts
        cursor.execute("""
            SELECT session_id FROM PersonalTrainingSession
            WHERE trainer_id = %s 
              AND session_date = %s
              AND status = 'Scheduled'
              AND (
                  (start_time <= %s AND end_time > %s) OR
                  (start_time < %s AND end_time >= %s) OR
                  (start_time >= %s AND end_time <= %s)
              )
        """, (trainer_id, session_date, start_time, start_time,
              end_time, end_time, start_time, end_time))

        if cursor.fetchone():
            print("❌ Error: Trainer already has a session at this time!")
            return

        # Find available room
        cursor.execute("""
            SELECT room_id FROM Room
            WHERE room_type = 'Personal Training'
              AND room_id NOT IN (
                  SELECT room_id FROM PersonalTrainingSession
                  WHERE session_date = %s
                    AND status = 'Scheduled'
                    AND (
                        (start_time <= %s AND end_time > %s) OR
                        (start_time < %s AND end_time >= %s) OR
                        (start_time >= %s AND end_time <= %s)
                    )
              )
            LIMIT 1
        """, (session_date, start_time, start_time, end_time, end_time,
              start_time, end_time))

        room = cursor.fetchone()
        if not room:
            print("❌ Error: No rooms available at this time!")
            return

        room_id = room[0]

        # Book the session
        cursor.execute("""
            INSERT INTO PersonalTrainingSession 
                (member_id, trainer_id, room_id, session_date, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
            RETURNING session_id
        """, (member_id, trainer_id, room_id, session_date, start_time, end_time))

        session_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✓ Session booked successfully! Session ID: {session_id}")
        print(f"  Room: {room_id}, Date: {
              session_date}, Time: {start_time}-{end_time}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def register_for_class(member_id):
    """Member Function (Bonus): Register for Group Class"""
    print("\n=== Register for Group Class ===")

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Show upcoming classes with availability
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.schedule_date, c.start_time, c.end_time,
                   t.first_name || ' ' || t.last_name as trainer_name,
                   c.current_enrollment, c.capacity,
                   (c.capacity - c.current_enrollment) as spots_left
            FROM Class c
            JOIN Trainer t ON c.trainer_id = t.trainer_id
            WHERE c.schedule_date >= CURRENT_DATE
              AND c.status = 'Scheduled'
              AND c.current_enrollment < c.capacity
            ORDER BY c.schedule_date, c.start_time
        """)

        classes = cursor.fetchall()
        if not classes:
            print("No classes available for registration.")
            return

        print("\nAvailable Classes:")
        for cls in classes:
            print(f"  {cls[0]}. {cls[1]} - {cls[2]} at {cls[3]}")
            print(f"      Trainer: {cls[5]}, Spots: {
                  cls[8]}/{cls[7]} available")

        class_id = int(input("\nSelect Class ID: "))

        # Check if already registered
        cursor.execute("""
            SELECT registration_id FROM ClassRegistration
            WHERE member_id = %s AND class_id = %s
        """, (member_id, class_id))

        if cursor.fetchone():
            print("❌ Error: Already registered for this class!")
            return

        # Register for class (trigger will update enrollment count)
        cursor.execute("""
            INSERT INTO ClassRegistration (member_id, class_id, status)
            VALUES (%s, %s, 'Registered')
            RETURNING registration_id
        """, (member_id, class_id))

        reg_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✓ Successfully registered! Registration ID: {reg_id}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


# ============================================================================
# TRAINER FUNCTIONS (2 operations required)
# ============================================================================

def set_trainer_availability(trainer_id):
    """Trainer Function 1: Set Availability Schedule"""
    print("\n=== Set Trainer Availability ===")

    day_of_week = input("Day of Week (Monday-Sunday): ").strip()
    start_time = input("Start Time (HH:MM): ").strip()
    end_time = input("End Time (HH:MM): ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Check for overlapping availability
        cursor.execute("""
            SELECT availability_id FROM TrainerAvailability
            WHERE trainer_id = %s 
              AND day_of_week = %s
              AND (
                  (start_time <= %s AND end_time > %s) OR
                  (start_time < %s AND end_time >= %s) OR
                  (start_time >= %s AND end_time <= %s)
              )
        """, (trainer_id, day_of_week, start_time, start_time,
              end_time, end_time, start_time, end_time))

        if cursor.fetchone():
            print("❌ Error: Overlapping availability exists!")
            return

        # Insert availability
        cursor.execute("""
            INSERT INTO TrainerAvailability (trainer_id, day_of_week, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            RETURNING availability_id
        """, (trainer_id, day_of_week, start_time, end_time))

        avail_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✓ Availability set successfully! ID: {avail_id}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def view_trainer_schedule(trainer_id):
    """Trainer Function 2: View Assigned Sessions and Classes"""
    print("\n=== Trainer Schedule ===")

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Show personal training sessions
        print("\n📋 PERSONAL TRAINING SESSIONS:")
        cursor.execute("""
            SELECT pts.session_date, pts.start_time, pts.end_time,
                   m.first_name || ' ' || m.last_name as member_name,
                   r.room_name, pts.status, pts.notes
            FROM PersonalTrainingSession pts
            JOIN Member m ON pts.member_id = m.member_id
            JOIN Room r ON pts.room_id = r.room_id
            WHERE pts.trainer_id = %s
              AND pts.session_date >= CURRENT_DATE
              AND pts.status = 'Scheduled'
            ORDER BY pts.session_date, pts.start_time
        """, (trainer_id,))

        sessions = cursor.fetchall()
        if sessions:
            for s in sessions:
                print(f"  • {s[0]} {s[1]}-{s[2]}: {s[3]} in {s[4]}")
                if s[6]:
                    print(f"    Notes: {s[6]}")
        else:
            print("  No upcoming sessions")

        # Show group classes
        print("\n👥 GROUP CLASSES:")
        cursor.execute("""
            SELECT c.class_name, c.schedule_date, c.start_time, c.end_time,
                   r.room_name, c.current_enrollment, c.capacity
            FROM Class c
            JOIN Room r ON c.room_id = r.room_id
            WHERE c.trainer_id = %s
              AND c.schedule_date >= CURRENT_DATE
              AND c.status = 'Scheduled'
            ORDER BY c.schedule_date, c.start_time
        """, (trainer_id,))

        classes = cursor.fetchall()
        if classes:
            for cls in classes:
                print(f"  • {cls[0]}: {cls[1]} {cls[2]}-{cls[3]}")
                print(f"    Room: {cls[4]}, Enrollment: {cls[5]}/{cls[6]}")
        else:
            print("  No upcoming classes")

        # Show availability schedule
        print("\n⏰ YOUR AVAILABILITY:")
        cursor.execute("""
            SELECT day_of_week, start_time, end_time
            FROM TrainerAvailability
            WHERE trainer_id = %s
            ORDER BY 
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                END,
                start_time
        """, (trainer_id,))

        avails = cursor.fetchall()
        if avails:
            for a in avails:
                print(f"  • {a[0]}: {a[1]} - {a[2]}")
        else:
            print("  No availability set")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def member_search_by_trainer(trainer_id):
    """Trainer Function (Bonus): Search and View Member Information"""
    print("\n=== Member Search ===")

    search_name = input("Enter member name to search: ").strip().lower()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Find members who have sessions with this trainer
        cursor.execute("""
            SELECT DISTINCT m.member_id, m.first_name, m.last_name, m.email
            FROM Member m
            JOIN PersonalTrainingSession pts ON m.member_id = pts.member_id
            WHERE pts.trainer_id = %s
              AND (LOWER(m.first_name) LIKE %s OR LOWER(m.last_name) LIKE %s)
        """, (trainer_id, f'%{search_name}%', f'%{search_name}%'))

        members = cursor.fetchall()
        if not members:
            print("No members found.")
            return

        print("\nFound Members:")
        for m in members:
            print(f"  {m[0]}. {m[1]} {m[2]} ({m[3]})")

        member_id = int(input("\nSelect Member ID to view details: "))

        # Get member details
        cursor.execute("""
            SELECT m.first_name, m.last_name, m.email, m.date_of_birth, m.phone
            FROM Member m
            WHERE m.member_id = %s
        """, (member_id,))

        member = cursor.fetchone()
        if member:
            print(f"\n👤 {member[0]} {member[1]}")
            print(f"   Email: {member[2]}")
            print(f"   DOB: {member[3]}")
            print(f"   Phone: {member[4]}")

            # Get latest health metric
            cursor.execute("""
                SELECT weight, heart_rate, recorded_date
                FROM HealthMetric
                WHERE member_id = %s
                ORDER BY recorded_date DESC
                LIMIT 1
            """, (member_id,))

            metric = cursor.fetchone()
            if metric:
                print(f"\n📊 Latest Metrics ({metric[2]}):")
                print(f"   Weight: {metric[0]} lbs")
                print(f"   Heart Rate: {metric[1]} bpm")

            # Get active goals
            cursor.execute("""
                SELECT goal_type, current_value, target_value, target_date
                FROM FitnessGoal
                WHERE member_id = %s AND status = 'Active'
            """, (member_id,))

            goals = cursor.fetchall()
            if goals:
                print("\n🎯 Active Goals:")
                for g in goals:
                    print(f"   - {g[0]}: {g[1]}/{g[2]} (Target: {g[3]})")
        else:
            print("Member details not found.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


# ============================================================================
# ADMIN FUNCTIONS (2 operations required)
# ============================================================================

def manage_room_booking():
    """Admin Function 1: Room Booking Management"""
    print("\n=== Room Booking Management ===")
    print("1. View Room Schedule")
    print("2. Book Room for Class")

    choice = input("\nSelect option: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        if choice == '1':
            # View room schedule
            room_date = input(
                "Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not room_date:
                room_date = date.today().strftime('%Y-%m-%d')

            print(f"\n📅 Room Schedule for {room_date}:")

            # Classes
            cursor.execute("""
                SELECT r.room_name, c.class_name, c.start_time, c.end_time,
                       t.first_name || ' ' || t.last_name as trainer
                FROM Class c
                JOIN Room r ON c.room_id = r.room_id
                JOIN Trainer t ON c.trainer_id = t.trainer_id
                WHERE c.schedule_date = %s AND c.status = 'Scheduled'
                ORDER BY r.room_name, c.start_time
            """, (room_date,))

            classes = cursor.fetchall()
            if classes:
                print("\nClasses:")
                for cls in classes:
                    print(f"  {cls[0]}: {
                          cls[1]} ({cls[2]}-{cls[3]}) - {cls[4]}")

            # Personal Training Sessions
            cursor.execute("""
                SELECT r.room_name, pts.start_time, pts.end_time,
                       t.first_name || ' ' || t.last_name as trainer,
                       m.first_name || ' ' || m.last_name as member
                FROM PersonalTrainingSession pts
                JOIN Room r ON pts.room_id = r.room_id
                JOIN Trainer t ON pts.trainer_id = t.trainer_id
                JOIN Member m ON pts.member_id = m.member_id
                WHERE pts.session_date = %s AND pts.status = 'Scheduled'
                ORDER BY r.room_name, pts.start_time
            """, (room_date,))

            sessions = cursor.fetchall()
            if sessions:
                print("\nPersonal Training Sessions:")
                for s in sessions:
                    print(f"  {s[0]}: {s[1]}-{s[2]} - {s[3]} with {s[4]}")

            if not classes and not sessions:
                print("  No bookings for this date")

        elif choice == '2':
            print("Room booking for classes is handled through Class Management")

        else:
            print("Invalid option")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def manage_equipment():
    """Admin Function 2: Equipment Maintenance Management"""
    print("\n=== Equipment Maintenance ===")
    print("1. View All Equipment")
    print("2. Log Maintenance Issue")
    print("3. Update Equipment Status")

    choice = input("\nSelect option: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        if choice == '1':
            # View all equipment
            cursor.execute("""
                SELECT e.equipment_id, e.equipment_name, r.room_name, e.status,
                       e.last_maintenance_date, e.maintenance_notes
                FROM Equipment e
                LEFT JOIN Room r ON e.room_id = r.room_id
                ORDER BY e.status DESC, e.equipment_name
            """)

            equipment = cursor.fetchall()
            print("\n🔧 Equipment List:")
            for eq in equipment:
                status_icon = "✓" if eq[3] == "Operational" else "⚠"
                print(f"  {status_icon} [{eq[0]}] {
                      eq[1]} - {eq[2] if eq[2] else 'No Room'}")
                print(f"       Status: {eq[3]}, Last Maintenance: {
                      eq[4] if eq[4] else 'Never'}")
                if eq[5]:
                    print(f"       Notes: {eq[5]}")

        elif choice == '2':
            # Log maintenance issue
            equipment_id = int(input("Equipment ID: "))
            issue = input("Describe the issue: ").strip()

            cursor.execute("""
                UPDATE Equipment
                SET status = 'Under Maintenance',
                    maintenance_notes = %s,
                    last_maintenance_date = CURRENT_DATE
                WHERE equipment_id = %s
            """, (issue, equipment_id))

            conn.commit()
            print("✓ Maintenance issue logged successfully!")

        elif choice == '3':
            # Update equipment status
            equipment_id = int(input("Equipment ID: "))
            print("\nStatus Options: Operational, Under Maintenance, Out of Service")
            new_status = input("New Status: ").strip()
            notes = input("Notes (optional): ").strip()

            cursor.execute("""
                UPDATE Equipment
                SET status = %s,
                    maintenance_notes = %s,
                    last_maintenance_date = CURRENT_DATE
                WHERE equipment_id = %s
            """, (new_status, notes if notes else None, equipment_id))

            conn.commit()
            print("✓ Equipment status updated successfully!")

        else:
            print("Invalid option")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def manage_billing(member_id=None):
    """Admin Function (Bonus): Billing and Payment Management"""
    print("\n=== Billing & Payment Management ===")
    print("1. Generate Bill")
    print("2. Record Payment")
    print("3. View Member Bills")

    choice = input("\nSelect option: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        if choice == '1':
            # Generate bill
            if not member_id:
                member_id = int(input("Member ID: "))

            description = input(
                "Description (e.g., Monthly Membership): ").strip()
            amount = float(input("Amount: $"))
            due_days = int(input("Days until due: "))

            cursor.execute("""
                INSERT INTO Bill (member_id, due_date, total_amount, description)
                VALUES (%s, CURRENT_DATE + INTERVAL '%s days', %s, %s)
                RETURNING bill_id
            """, (member_id, due_days, amount, description))

            bill_id = cursor.fetchone()[0]
            conn.commit()

            print(f"✓ Bill generated successfully! Bill ID: {bill_id}")

        elif choice == '2':
            # Record payment
            bill_id = int(input("Bill ID: "))
            amount = float(input("Payment Amount: $"))
            method = input(
                "Payment Method (Cash/Credit Card/Debit Card/Bank Transfer): ").strip()
            reference = input("Transaction Reference (optional): ").strip()

            # Check bill exists and get details
            cursor.execute("""
                SELECT total_amount, amount_paid, status
                FROM Bill
                WHERE bill_id = %s
            """, (bill_id,))

            bill = cursor.fetchone()
            if not bill:
                print("❌ Bill not found!")
                return

            remaining = bill[0] - bill[1]
            if amount > remaining:
                print(f"⚠ Warning: Payment exceeds remaining balance of ${
                      remaining:.2f}")

            # Record payment (trigger will update bill)
            cursor.execute("""
                INSERT INTO Payment (bill_id, amount, payment_method, transaction_reference)
                VALUES (%s, %s, %s, %s)
                RETURNING payment_id
            """, (bill_id, amount, method, reference if reference else None))

            payment_id = cursor.fetchone()[0]
            conn.commit()

            print(f"✓ Payment recorded successfully! Payment ID: {
                  payment_id}")

        elif choice == '3':
            # View member bills
            if not member_id:
                member_id = int(input("Member ID: "))

            cursor.execute("""
                SELECT bill_id, bill_date, due_date, total_amount, amount_paid, 
                       status, description
                FROM Bill
                WHERE member_id = %s
                ORDER BY bill_date DESC
            """, (member_id,))

            bills = cursor.fetchall()
            if bills:
                print(f"\n💰 Bills for Member {member_id}:")
                for b in bills:
                    status_icon = "✓" if b[5] == "Paid" else "⏳"
                    print(f"  {status_icon} [{b[0]}] {b[6]}")
                    print(f"      Date: {b[1]}, Due: {b[2]}, Status: {b[5]}")
                    print(f"      Amount: ${b[3]:.2f}, Paid: ${
                          b[4]:.2f}, Balance: ${b[3] - b[4]:.2f}")
            else:
                print("No bills found for this member.")

        else:
            print("Invalid option")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def member_menu():
    """Member interface"""
    print("\n" + "=" * 60)
    print("MEMBER MENU")
    print("=" * 60)

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT member_id, first_name, last_name
            FROM Member
            WHERE email = %s AND password = %s
        """, (email, password))

        user = cursor.fetchone()
        if not user:
            print("❌ Invalid credentials!")
            return

        member_id, first_name, last_name = user
        print(f"\n✓ Welcome, {first_name} {last_name}!")

        while True:
            print(f"\n{'=' * 60}")
            print("1. View Dashboard")
            print("2. Update Profile / Manage Goals / Add Health Metric")
            print("3. Schedule Personal Training Session")
            print("4. Register for Group Class")
            print("5. Logout")

            choice = input("\nSelect option: ").strip()

            if choice == '1':
                member_dashboard(member_id)
            elif choice == '2':
                profile_management(member_id)
            elif choice == '3':
                schedule_personal_training(member_id)
            elif choice == '4':
                register_for_class(member_id)
            elif choice == '5':
                print("Logging out...")
                break
            else:
                print("Invalid option")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def trainer_menu():
    """Trainer interface"""
    print("\n" + "=" * 60)
    print("TRAINER MENU")
    print("=" * 60)

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trainer_id, first_name, last_name
            FROM Trainer
            WHERE email = %s AND password = %s
        """, (email, password))

        user = cursor.fetchone()
        if not user:
            print("❌ Invalid credentials!")
            return

        trainer_id, first_name, last_name = user
        print(f"\n✓ Welcome, {first_name} {last_name}!")

        while True:
            print(f"\n{'=' * 60}")
            print("1. View My Schedule")
            print("2. Set Availability")
            print("3. Search Member")
            print("4. Logout")

            choice = input("\nSelect option: ").strip()

            if choice == '1':
                view_trainer_schedule(trainer_id)
            elif choice == '2':
                set_trainer_availability(trainer_id)
            elif choice == '3':
                member_search_by_trainer(trainer_id)
            elif choice == '4':
                print("Logging out...")
                break
            else:
                print("Invalid option")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def admin_menu():
    """Admin interface"""
    print("\n" + "=" * 60)
    print("ADMIN MENU")
    print("=" * 60)

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT admin_id, first_name, last_name
            FROM AdminStaff
            WHERE email = %s AND password = %s
        """, (email, password))

        user = cursor.fetchone()
        if not user:
            print("❌ Invalid credentials!")
            return

        admin_id, first_name, last_name = user
        print(f"\n✓ Welcome, {first_name} {last_name}!")

        while True:
            print(f"\n{'=' * 60}")
            print("1. Manage Room Bookings")
            print("2. Manage Equipment Maintenance")
            print("3. Manage Billing & Payments")
            print("4. Logout")

            choice = input("\nSelect option: ").strip()

            if choice == '1':
                manage_room_booking()
            elif choice == '2':
                manage_equipment()
            elif choice == '3':
                manage_billing()
            elif choice == '4':
                print("Logging out...")
                break
            else:
                print("Invalid option")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)


def main():
    """Main application entry point"""
    print("\n" + "=" * 60)
    print(" HEALTH & FITNESS CLUB MANAGEMENT SYSTEM")
    print("=" * 60)

    # Initialize database connection
    db.initialize_pool()

    try:
        while True:
            print("\n" + "=" * 60)
            print("MAIN MENU")
            print("=" * 60)
            print("1. Member Login")
            print("2. Member Registration")
            print("3. Trainer Login")
            print("4. Admin Login")
            print("5. Exit")

            choice = input("\nSelect option: ").strip()

            if choice == '1':
                member_menu()
            elif choice == '2':
                member_registration()
            elif choice == '3':
                trainer_menu()
            elif choice == '4':
                admin_menu()
            elif choice == '5':
                print("\nThank you for using the Fitness Club Management System!")
                break
            else:
                print("Invalid option. Please try again.")

    finally:
        # Close database connections
        db.close_all_connections()
        print("Database connections closed.")


if __name__ == "__main__":
    main()
