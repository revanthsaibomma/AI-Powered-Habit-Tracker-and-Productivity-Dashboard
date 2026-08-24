from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, date, timedelta
from pathlib import Path
import sqlite3

app = Flask(__name__)
CORS(app)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "habit_tracker.db"

DATABASE_DIR.mkdir(exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_db()
    cursor = connection.cursor()

    # Habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            frequency TEXT DEFAULT 'Daily',
            target INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
    """)

    # Habit completion history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, completed_date)
        )
    """)

    # Tasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_streak(habit_id):

    connection = get_db()

    rows = connection.execute("""
        SELECT completed_date
        FROM habit_logs
        WHERE habit_id = ?
        ORDER BY completed_date DESC
    """, (habit_id,)).fetchall()

    connection.close()

    if not rows:
        return 0

    dates = {
        datetime.strptime(row["completed_date"], "%Y-%m-%d").date()
        for row in rows
    }

    current_day = date.today()
    streak = 0

    while current_day in dates:

        streak += 1
        current_day -= timedelta(days=1)

    return streak


def get_productivity():

    connection = get_db()

    total_habits = connection.execute("""
        SELECT COUNT(*) AS count
        FROM habits
        WHERE active = 1
    """).fetchone()["count"]

    completed_today = connection.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed_date = ?
    """, (date.today().isoformat(),)).fetchone()[0]

    total_tasks = connection.execute("""
        SELECT COUNT(*)
        FROM tasks
    """).fetchone()[0]

    completed_tasks = connection.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 1
    """).fetchone()[0]

    connection.close()

    total_items = total_habits + total_tasks

    completed_items = completed_today + completed_tasks

    if total_items == 0:
        return 0

    return round(
        (completed_items / total_items) * 100,
        2
    )


# ============================================================
# MAIN PAGE
# ============================================================

@app.route("/")
def dashboard():

    return render_template("dashboard.html")


# ============================================================
# HABIT APIs
# ============================================================

@app.route("/api/habits", methods=["GET"])
def get_habits():

    connection = get_db()

    habits = connection.execute("""
        SELECT *
        FROM habits
        WHERE active = 1
        ORDER BY id DESC
    """).fetchall()

    result = []

    for habit in habits:

        today = date.today().isoformat()

        completed_today = connection.execute("""
            SELECT id
            FROM habit_logs
            WHERE habit_id = ?
            AND completed_date = ?
        """, (
            habit["id"],
            today
        )).fetchone()

        result.append({
            "id": habit["id"],
            "name": habit["name"],
            "category": habit["category"],
            "frequency": habit["frequency"],
            "target": habit["target"],
            "completed_today": completed_today is not None,
            "streak": calculate_streak(habit["id"]),
            "created_at": habit["created_at"]
        })

    connection.close()

    return jsonify(result)


@app.route("/api/habits", methods=["POST"])
def create_habit():

    data = request.get_json()

    name = data.get("name", "").strip()
    category = data.get("category", "General")
    frequency = data.get("frequency", "Daily")

    if not name:
        return jsonify({
            "error": "Habit name is required"
        }), 400

    connection = get_db()

    connection.execute("""
        INSERT INTO habits
        (
            name,
            category,
            frequency,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        category,
        frequency,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Habit created successfully"
    }), 201


@app.route("/api/habits/<int:habit_id>/complete", methods=["POST"])
def complete_habit(habit_id):

    today = date.today().isoformat()

    connection = get_db()

    try:

        connection.execute("""
            INSERT INTO habit_logs
            (
                habit_id,
                completed_date
            )
            VALUES (?, ?)
        """, (
            habit_id,
            today
        ))

        connection.commit()

        message = "Habit completed"

    except sqlite3.IntegrityError:

        connection.execute("""
            DELETE FROM habit_logs
            WHERE habit_id = ?
            AND completed_date = ?
        """, (
            habit_id,
            today
        ))

        connection.commit()

        message = "Habit marked incomplete"

    connection.close()

    return jsonify({
        "message": message
    })


@app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM habit_logs
        WHERE habit_id = ?
    """, (habit_id,))

    connection.execute("""
        UPDATE habits
        SET active = 0
        WHERE id = ?
    """, (habit_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Habit deleted successfully"
    })


# ============================================================
# TASK APIs
# ============================================================

@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    connection = get_db()

    tasks = connection.execute("""
        SELECT *
        FROM tasks
        ORDER BY
            completed ASC,
            id DESC
    """).fetchall()

    result = [dict(task) for task in tasks]

    connection.close()

    return jsonify(result)


@app.route("/api/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "")
    priority = data.get("priority", "Medium")
    due_date = data.get("due_date")

    if not title:
        return jsonify({
            "error": "Task title is required"
        }), 400

    connection = get_db()

    connection.execute("""
        INSERT INTO tasks
        (
            title,
            description,
            priority,
            due_date,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        description,
        priority,
        due_date,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Task created successfully"
    }), 201


@app.route("/api/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):

    connection = get_db()

    connection.execute("""
        UPDATE tasks
        SET completed =
            CASE
                WHEN completed = 1 THEN 0
                ELSE 1
            END
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Task status updated"
    })


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Task deleted successfully"
    })


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@app.route("/api/dashboard")
def dashboard_statistics():

    connection = get_db()

    total_habits = connection.execute("""
        SELECT COUNT(*)
        FROM habits
        WHERE active = 1
    """).fetchone()[0]

    completed_habits = connection.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed_date = ?
    """, (
        date.today().isoformat(),
    )).fetchone()[0]

    total_tasks = connection.execute("""
        SELECT COUNT(*)
        FROM tasks
    """).fetchone()[0]

    completed_tasks = connection.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 1
    """).fetchone()[0]

    longest_streak = 0

    habit_ids = connection.execute("""
        SELECT id
        FROM habits
        WHERE active = 1
    """).fetchall()

    connection.close()

    for habit in habit_ids:

        streak = calculate_streak(habit["id"])

        longest_streak = max(
            longest_streak,
            streak
        )

    productivity = get_productivity()

    return jsonify({

        "total_habits": total_habits,

        "completed_habits": completed_habits,

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "productivity": productivity,

        "longest_streak": longest_streak

    })


# ============================================================
# ANALYTICS
# ============================================================

@app.route("/api/analytics")
def analytics():

    connection = get_db()

    result = []

    for days_ago in range(6, -1, -1):

        current_date = (
            date.today()
            - timedelta(days=days_ago)
        ).isoformat()

        habits_completed = connection.execute("""
            SELECT COUNT(*)
            FROM habit_logs
            WHERE completed_date = ?
        """, (
            current_date,
        )).fetchone()[0]

        tasks_completed = connection.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE completed = 1
            AND DATE(created_at) <= ?
        """, (
            current_date,
        )).fetchone()[0]

        result.append({

            "date": current_date,

            "habits": habits_completed,

            "tasks": tasks_completed

        })

    connection.close()

    return jsonify(result)


# ============================================================
# AI PRODUCTIVITY INSIGHTS
# ============================================================

@app.route("/api/ai-insights")
def ai_insights():

    connection = get_db()

    total_habits = connection.execute("""
        SELECT COUNT(*)
        FROM habits
        WHERE active = 1
    """).fetchone()[0]

    completed_today = connection.execute("""
        SELECT COUNT(*)
        FROM habit_logs
        WHERE completed_date = ?
    """, (
        date.today().isoformat(),
    )).fetchone()[0]

    pending_tasks = connection.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 0
    """).fetchone()[0]

    connection.close()

    insights = []

    if total_habits == 0:

        insights.append(
            "Start by creating your first habit."
        )

    elif completed_today == total_habits:

        insights.append(
            "Excellent! You completed all your habits today."
        )

    elif completed_today > 0:

        insights.append(
            f"You completed {completed_today} of "
            f"{total_habits} habits today. "
            "Keep going!"
        )

    else:

        insights.append(
            "You haven't completed any habits today. "
            "Start with one small habit."
        )

    if pending_tasks > 5:

        insights.append(
            "You have several pending tasks. "
            "Consider prioritizing the most important ones."
        )

    elif pending_tasks > 0:

        insights.append(
            f"You have {pending_tasks} pending tasks. "
            "Try completing the highest-priority task first."
        )

    else:

        insights.append(
            "Great job! You have no pending tasks."
        )

    insights.append(
        "Consistency is more important than perfection. "
        "Focus on completing small actions every day."
    )

    return jsonify({
        "insights": insights
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("\n========================================")
    print(" AI HABIT TRACKER")
    print("========================================")
    print(" Server: http://127.0.0.1:5000")
    print("========================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )