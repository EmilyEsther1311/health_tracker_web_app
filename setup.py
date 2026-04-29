from datetime import datetime, timedelta
from app import db
from app.models import *

def reset_database():
    """Drop all tables, recreate them, and insert basic test data."""
    db.drop_all()
    db.create_all()

    # --- Create Users ---
    alice = User(username="alice", email="alice@example.com")
    alice.set_password("password123")

    bob = User(username="bob", email="bob@example.com")
    bob.set_password("password123")

    db.session.add_all([alice, bob])
    db.session.commit()

    # --- Create Support Groups ---
    group1 = SupportGroup(name='Fitness Fanatics', leader=alice)
    group2 = SupportGroup(name='Workout Warriors', leader=alice)

    db.session.add_all([group1, group2])
    db.session.commit()

    # --- Create Exercise Types ---
    walk = ExerciseType(description="Walking", duration=30, intensity=1, attachment_filename='dynamic_warmup.jpg')
    run = ExerciseType(description="Running", duration=20, intensity=3, attachment_filename='interval_session.jpg')
    cycle = ExerciseType(description="Cycling", duration=45, intensity=2, attachment_filename='cycling_warmup.jpg')

    db.session.add_all([walk, run, cycle])
    db.session.commit()

    # --- Create Activities ---
    now = datetime.utcnow()

    a1 = Activity(
        user=alice,
        exercise_type=walk,
        start_time=now - timedelta(hours=2),
        end_time=now - timedelta(hours=1, minutes=30),
        notes="This was easy!"
    )

    a2 = Activity(
        user=bob,
        exercise_type=run,
        start_time=now - timedelta(days=1, hours=1),
        end_time=now - timedelta(days=1),
        notes="This was hard!"
    )

    db.session.add_all([a1, a2])
    db.session.commit()

    # --- Create Body Measurements ---
    m1 = BodyMeasurement(
        user=alice,
        timestamp=now - timedelta(days=1),
        weight=65.2,
        pulse=72
    )

    m2 = BodyMeasurement(
        user=bob,
        timestamp=now - timedelta(days=2),
        weight=82.5,
        pulse=78
    )

    db.session.add_all([m1, m2])
    db.session.commit()

    print("Database reset and test data inserted.")