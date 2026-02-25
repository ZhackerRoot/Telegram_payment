from nicegui import ui
import requests
import os

# ================= CONFIG =================

SERVER = "https://skynet-skynet.up.railway.app/"
ADMIN_KEY = "SKYN3T_SUPER_ADMIN_2026"

# ================= API =================

def get_users():
    r = requests.get(
        f"{SERVER}/admin/users",
        headers={"x-admin-key": ADMIN_KEY},
        timeout=10
    )
    return r.json()


def activate_vip(username):
    requests.post(
        f"{SERVER}/admin/vip",
        headers={"x-admin-key": ADMIN_KEY},
        json={"username": username}
    )
    load_table()


def activate_standard(username):
    requests.post(
        f"{SERVER}/admin/standard",
        headers={"x-admin-key": ADMIN_KEY},
        json={"username": username}
    )
    load_table()


def block_user(username):
    requests.post(
        f"{SERVER}/admin/block",
        headers={"x-admin-key": ADMIN_KEY},
        json={"username": username}
    )
    load_table()


# ================= TABLE =================

table = None


def load_table():
    users = get_users()

    rows = []
    for u in users:
        rows.append({
            "username": u["username"],
            "plan": u["plan"],
            "active": "🟢" if u["active"] else "🔴",
        })

    table.rows = rows
    table.update()


# ================= UI =================

ui.label("🚀 SkyNet Admin Panel").classes("text-h4")

columns = [
    {"name": "username", "label": "User", "field": "username"},
    {"name": "plan", "label": "Plan", "field": "plan"},
    {"name": "active", "label": "Active", "field": "active"},
    {"name": "actions", "label": "Actions", "field": "actions"},
]

table = ui.table(columns=columns, rows=[]).classes("w-full")


# ===== ACTION BUTTONS =====

@table.add_slot('body-cell-actions')
def _(row):
    with ui.row():
        ui.button(
            "VIP",
            color="green",
            on_click=lambda: activate_vip(row["username"])
        )

        ui.button(
            "STANDARD",
            color="blue",
            on_click=lambda: activate_standard(row["username"])
        )

        ui.button(
            "BLOCK",
            color="red",
            on_click=lambda: block_user(row["username"])
        )


# ===== REFRESH =====

ui.button("🔄 Refresh", on_click=load_table)

# auto refresh har 10s
ui.timer(10, load_table)

load_table()

ui.run(port=8080)