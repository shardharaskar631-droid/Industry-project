from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("jobs.db")

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL, role TEXT NOT NULL,
            applied_on TEXT NOT NULL, status TEXT NOT NULL,
            follow_up TEXT DEFAULT '', notes TEXT DEFAULT ''
        )""")

PAGE = """
<!doctype html><html><head><title>Job Tracker</title>
<style>
body{font:16px Arial;max-width:1000px;margin:35px auto;padding:0 16px;background:#f5f7fb;color:#172033}
.card{background:white;padding:18px;border-radius:12px;margin:14px 0;box-shadow:0 2px 10px #0001}
input,select,textarea,button{padding:10px;margin:5px;border:1px solid #ccd2df;border-radius:6px}
button{background:#2457d6;color:white;border:0;cursor:pointer}table{width:100%;border-collapse:collapse}
td,th{text-align:left;padding:10px;border-bottom:1px solid #e5e8ef}
.stats{display:flex;gap:12px;flex-wrap:wrap}.stat{background:#eaf0ff;padding:12px 18px;border-radius:8px}
</style></head><body><h1>Job Application Tracker</h1>
<div class="stats">{% for s,n in stats.items() %}<div class="stat"><b>{{n}}</b> {{s}}</div>{% endfor %}</div>
<div class="card"><h2>Add application</h2><form method="post" action="/add">
<input name="company" placeholder="Company" required><input name="role" placeholder="Role" required>
<input name="applied_on" type="date" required>
<select name="status">{% for s in statuses %}<option>{{s}}</option>{% endfor %}</select>
<input name="follow_up" type="date" placeholder="Follow-up">
<input name="notes" placeholder="Notes"><button>Add</button></form></div>
<div class="card"><h2>Applications</h2><table><tr><th>Company</th><th>Role</th><th>Applied</th><th>Status</th><th>Follow-up</th><th>Action</th></tr>
{% for j in jobs %}<tr><td>{{j.company}}</td><td>{{j.role}}</td><td>{{j.applied_on}}</td><td>
<form method="post" action="/status/{{j.id}}"><select name="status" onchange="this.form.submit()">{% for s in statuses %}<option {% if s==j.status %}selected{% endif %}>{{s}}</option>{% endfor %}</select></form>
</td><td>{{j.follow_up}}</td><td><form method="post" action="/delete/{{j.id}}"><button>Delete</button></form></td></tr>{% endfor %}
</table></div></body></html>
"""
STATUSES = ["Applied", "Assessment", "Interview", "Offer", "Rejected"]

@app.get("/")
def home():
    with connect() as db:
        jobs = db.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
        stats = {s: db.execute("SELECT COUNT(*) FROM applications WHERE status=?", (s,)).fetchone()[0] for s in STATUSES}
    return render_template_string(PAGE, jobs=jobs, stats=stats, statuses=STATUSES)

@app.post("/add")
def add():
    data = [request.form.get(k, "").strip() for k in ("company","role","applied_on","status","follow_up","notes")]
    with connect() as db:
        db.execute("INSERT INTO applications(company,role,applied_on,status,follow_up,notes) VALUES(?,?,?,?,?,?)", data)
    return redirect(url_for("home"))

@app.post("/status/<int:job_id>")
def update_status(job_id):
    with connect() as db:
        db.execute("UPDATE applications SET status=? WHERE id=?", (request.form["status"], job_id))
    return redirect(url_for("home"))

@app.post("/delete/<int:job_id>")
def delete(job_id):
    with connect() as db:
        db.execute("DELETE FROM applications WHERE id=?", (job_id,))
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
