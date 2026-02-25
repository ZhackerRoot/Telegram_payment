from fastapi import FastAPI, Request
import psycopg2
import os
import requests
from datetime import datetime, timedelta
from fastapi import Header

app = FastAPI()

# =============================
# CONFIG
# =============================
DATABASE_URL = os.getenv("DATABASE_URL")
print("Database: ", DATABASE_URL)



TRIAL_DURATION = 600  # 10 min


# =============================
# DATABASE CONNECTION
# =============================
def get_connection():
    return psycopg2.connect(DATABASE_URL)


# =============================
# HEALTH CHECK
# =============================
@app.get("/")
def health():
    return {"status": "server running"}


# =============================
# VERIFY USER (BOT START CHECK)
# =============================
@app.post("/verify")
def verify(data: dict):

    username = data.get("username")

    if not username:
        return {"status": "invalid"}

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT plan,
               is_active,
               subscription_end,
               allow_demo,
               trial_start,
               trial_used
        FROM users
        WHERE username=%s
    """, (username,))

    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return {"status": "not_found"}

    plan, is_active, sub_end, allow_demo, trial_start, trial_used = row
    now = datetime.utcnow()

    # =========================
    # BLOCKED USER
    # =========================
    if not is_active:
        cur.close()
        conn.close()
        return {"status": "blocked"}

    # =========================
    # PAID USERS (VIP/STANDARD/ADMIN)
    # =========================
    if plan in ["admin", "vip", "standard"]:

        # subscription expired
        if sub_end and sub_end < now:
            cur.close()
            conn.close()
            return {"status": "expired"}

        # 🔥 IMPORTANT: TRIAL DELETE
        cur.execute("""
            UPDATE users
            SET trial_start=NULL,
                trial_used=TRUE
            WHERE username=%s
        """, (username,))
        conn.commit()

        cur.close()
        conn.close()

        return {
            "status": "active",
            "plan": plan,
            "allow_demo": allow_demo
        }

    # =========================
    # TRIAL SYSTEM
    # =========================
    if plan == "none":

        # Trial already used → BLOCK
        if trial_used:
            cur.close()
            conn.close()
            return {"status": "trial_expired"}

        # Start trial once
        if not trial_start:
            trial_start = now
            cur.execute("""
                UPDATE users
                SET trial_start=%s
                WHERE username=%s
            """, (trial_start, username))
            conn.commit()

        elapsed = (now - trial_start).total_seconds()

        if elapsed > TRIAL_DURATION:

            cur.execute("""
                UPDATE users
                SET trial_used=TRUE
                WHERE username=%s
            """, (username,))
            conn.commit()

            cur.close()
            conn.close()

            return {"status": "trial_expired"}

        remaining = TRIAL_DURATION - elapsed

        cur.close()
        conn.close()

        return {
            "status": "trial",
            "remaining": int(remaining)
        }

    cur.close()
    conn.close()

    return {"status": "invalid"}


# =============================
# HEARTBEAT (REALTIME CONTROL)
# Robot har 20s serverga uradi
# =============================
@app.post("/heartbeat")
def heartbeat(data: dict):

    username = data.get("username")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT is_active, subscription_end
        FROM users
        WHERE username=%s
    """, (username,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"status": "not_found"}

    is_active, sub_end = row
    now = datetime.utcnow()

    if not is_active:
        return {"status": "blocked"}

    if sub_end and sub_end < now:
        return {"status": "expired"}

    return {"status": "ok"}


@app.post("/create_user_request")
def create_request(data: dict):

    username = data["username"]
    plan = data["plan"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(username, plan, is_active)
        VALUES(%s,'none',FALSE)
        ON CONFLICT(username) DO NOTHING
    """,(username,))

    conn.commit()
    cur.close()
    conn.close()

    return {"status":"ok"}