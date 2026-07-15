import sqlite3
from datetime import datetime

DB_NAME = "93run.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# ======================================================
# CREATE TABLE
# ======================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS challenge_submissions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,

    activity TEXT NOT NULL,

    hours INTEGER NOT NULL,
    minutes INTEGER NOT NULL,

    notes TEXT,

    submission_message_id INTEGER,
    screenshot_message_id INTEGER,

    screenshot_url TEXT,

    status TEXT DEFAULT 'pending',

    created_at TEXT,
    verified_at TEXT

)
""")

conn.commit()

# ======================================================
# ADD SUBMISSION
# ======================================================

def add_submission(
    user_id,
    username,
    activity,
    hours,
    minutes,
    notes
):

    created = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO challenge_submissions
        (
            user_id,
            username,
            activity,
            hours,
            minutes,
            notes,
            created_at
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            username,
            activity,
            hours,
            minutes,
            notes,
            created
        )
    )

    conn.commit()

    return cursor.lastrowid


# ======================================================
# SAVE SUBMISSION MESSAGE
# ======================================================

def save_submission_message(
    submission_id,
    message_id
):

    cursor.execute(
        """
        UPDATE challenge_submissions
        SET submission_message_id=?
        WHERE id=?
        """,
        (
            message_id,
            submission_id
        )
    )

    conn.commit()


# ======================================================
# GET PENDING SUBMISSION
# ======================================================

def get_pending_submission(user_id):

    cursor.execute(
        """
        SELECT *
        FROM challenge_submissions
        WHERE
            user_id=?
            AND status='pending'
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    return cursor.fetchone()


# ======================================================
# VERIFY SUBMISSION
# ======================================================

def verify_submission(
    submission_id,
    screenshot_message_id,
    screenshot_url
):

    verified = datetime.utcnow().isoformat()

    cursor.execute(
        """
        UPDATE challenge_submissions
        SET

            screenshot_message_id=?,
            screenshot_url=?,
            status='verified',
            verified_at=?

        WHERE id=?
        """,
        (
            screenshot_message_id,
            screenshot_url,
            verified,
            submission_id
        )
    )

    conn.commit()


# ======================================================
# GET LEADERBOARD
# ======================================================

def get_leaderboard():

    cursor.execute(
        """
        SELECT

            user_id,

            SUM(hours * 60 + minutes) AS total_minutes

        FROM challenge_submissions

        WHERE status='verified'

        GROUP BY user_id

        ORDER BY total_minutes DESC
        """
    )

    return cursor.fetchall()

    # ======================================================
# GET USER STATS
# ======================================================

def get_user_stats(user_id):

    cursor.execute(
        """
        SELECT

            COUNT(*) as workouts,

            SUM(CASE WHEN activity='Run' THEN 1 ELSE 0 END) as runs,

            SUM(CASE WHEN activity='Walk' THEN 1 ELSE 0 END) as walks,

            SUM(CASE WHEN activity='Hike' THEN 1 ELSE 0 END) as hikes,

            COALESCE(SUM(hours * 60 + minutes),0) as total_minutes

        FROM challenge_submissions

        WHERE
            user_id=?
            AND status='verified'
        """,
        (user_id,)
    )

    return cursor.fetchone()


# ======================================================
# GET USER RANK
# ======================================================

def get_user_rank(user_id):

    cursor.execute(
        """
        SELECT
            user_id,
            SUM(hours * 60 + minutes) as total_minutes

        FROM challenge_submissions

        WHERE status='verified'

        GROUP BY user_id

        ORDER BY total_minutes DESC
        """
    )

    leaderboard = cursor.fetchall()

    for index, row in enumerate(leaderboard):

        if row[0] == user_id:
            return index + 1

    return None


# ======================================================
# GET LAST VERIFIED WORKOUT
# ======================================================

def get_last_workout(user_id):

    cursor.execute(
        """
        SELECT
            activity,
            hours,
            minutes,
            verified_at

        FROM challenge_submissions

        WHERE
            user_id=?
            AND status='verified'

        ORDER BY verified_at DESC

        LIMIT 1
        """,
        (user_id,)
    )

    return cursor.fetchone()

    cursor.execute(
        """
        SELECT

            username,

            SUM(hours * 60 + minutes) AS total_minutes

        FROM challenge_submissions

        WHERE status='verified'

        GROUP BY username

        ORDER BY total_minutes DESC
        """
    )

    return cursor.fetchall()
    # ======================================================
# ACHIEVEMENTS TABLE
# ======================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    achievement TEXT NOT NULL,

    earned_at TEXT NOT NULL
)
""")

conn.commit()


# ======================================================
# GIVE ACHIEVEMENT
# ======================================================

def give_achievement(user_id, achievement):

    cursor.execute(
        """
        SELECT id
        FROM achievements
        WHERE
            user_id=?
            AND achievement=?
        """,
        (
            user_id,
            achievement
        )
    )

    if cursor.fetchone():
        return False

    cursor.execute(
        """
        INSERT INTO achievements
        (
            user_id,
            achievement,
            earned_at
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            achievement,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()

    return True


# ======================================================
# GET ACHIEVEMENTS
# ======================================================

def get_achievements(user_id):

    cursor.execute(
        """
        SELECT achievement

        FROM achievements

        WHERE user_id=?

        ORDER BY earned_at
        """,
        (
            user_id,
        )
    )

    return cursor.fetchall()
    # ======================================================
# HAS BADGE
# ======================================================

def has_badge(user_id, badge):

    cursor.execute(
        """
        SELECT 1
        FROM achievements
        WHERE
            user_id=?
            AND achievement=?
        LIMIT 1
        """,
        (
            user_id,
            badge
        )
    )

    return cursor.fetchone() is not None
    from datetime import datetime, timedelta


# ======================================================
# GET USER STREAK
# ======================================================

def get_user_streak(user_id):

    cursor.execute(
        """
        SELECT DATE(verified_at)

        FROM challenge_submissions

        WHERE
            user_id=?
            AND status='verified'

        ORDER BY verified_at DESC
        """,
        (
            user_id,
        )
    )

    rows = cursor.fetchall()

    if not rows:
        return 0

    workout_days = {
        datetime.strptime(row[0], "%Y-%m-%d").date()
        for row in rows
    }

    today = datetime.utcnow().date()

    # Allow today's workout or yesterday's
    if today in workout_days:
        current_day = today
    elif (today - timedelta(days=1)) in workout_days:
        current_day = today - timedelta(days=1)
    else:
        return 0

    streak = 0

    while current_day in workout_days:
        streak += 1
        current_day -= timedelta(days=1)

    return streak