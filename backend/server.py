from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os, datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal.db')
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'job_seeker',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            type TEXT DEFAULT 'Full-time',
            status TEXT DEFAULT 'active',
            salary TEXT,
            posted_by INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(posted_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            applied_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    conn.commit()

    count = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if count == 0:
        users = [
            ('Priya Sharma', 'priya@example.com', 'admin'),
            ('Arjun Nair', 'arjun@example.com', 'recruiter'),
            ('Meera Patel', 'meera@example.com', 'job_seeker'),
            ('Rahul Gupta', 'rahul@example.com', 'job_seeker'),
            ('Sneha Reddy', 'sneha@example.com', 'job_seeker'),
            ('Vikram Singh', 'vikram@example.com', 'recruiter'),
            ('Ananya Krishnan', 'ananya@example.com', 'job_seeker'),
            ('Dev Malhotra', 'dev@example.com', 'job_seeker'),
            ('Kavya Iyer', 'kavya@example.com', 'job_seeker'),
            ('Ravi Teja', 'ravi@example.com', 'job_seeker'),
        ]
        c.executemany('INSERT INTO users (name, email, role) VALUES (?,?,?)', users)

        jobs = [
            ('Senior React Developer','TechCorp India','Engineering','Bangalore','Full-time','active','₹18-25 LPA',2),
            ('Data Scientist','Analytics Hub','Data Science','Hyderabad','Full-time','active','₹15-22 LPA',2),
            ('UI/UX Designer','Designify','Design','Mumbai','Full-time','active','₹10-15 LPA',6),
            ('Backend Engineer','CloudBase','Engineering','Pune','Full-time','active','₹20-30 LPA',2),
            ('Product Manager','StartupX','Management','Delhi','Full-time','closed','₹25-35 LPA',6),
            ('ML Engineer','AI Ventures','Data Science','Bangalore','Full-time','active','₹22-32 LPA',2),
            ('DevOps Engineer','InfraNet','Engineering','Chennai','Full-time','active','₹16-24 LPA',6),
            ('Content Writer','MediaPro','Marketing','Remote','Part-time','active','₹5-8 LPA',6),
            ('QA Engineer','QualityFirst','Engineering','Hyderabad','Full-time','closed','₹10-14 LPA',2),
            ('Finance Analyst','FinEdge','Finance','Mumbai','Full-time','active','₹12-18 LPA',6),
        ]
        c.executemany('INSERT INTO jobs (title,company,category,location,type,status,salary,posted_by) VALUES (?,?,?,?,?,?,?,?)', jobs)

        apps = [
            (1,3,'pending'),(1,4,'reviewed'),(1,5,'accepted'),
            (2,3,'pending'),(2,7,'pending'),(2,8,'reviewed'),
            (3,4,'accepted'),(3,9,'rejected'),
            (4,5,'pending'),(4,10,'pending'),(4,3,'reviewed'),
            (5,7,'rejected'),(5,8,'rejected'),
            (6,3,'pending'),(6,4,'reviewed'),(6,9,'pending'),(6,10,'accepted'),
            (7,5,'pending'),(7,8,'pending'),
            (8,7,'accepted'),
            (9,9,'rejected'),(9,10,'rejected'),
            (10,3,'pending'),(10,4,'pending'),
        ]
        c.executemany('INSERT INTO applications (job_id,user_id,status) VALUES (?,?,?)', apps)
        conn.commit()
        print("✅ Sample data seeded successfully!")
    conn.close()

# ─── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/api/stats')
def stats():
    conn = get_db(); c = conn.cursor()
    total_jobs = c.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    active_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE status='active'").fetchone()[0]
    total_users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_apps = c.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    apps_per_job = [dict(r) for r in c.execute("""
        SELECT j.title, COUNT(a.id) as count FROM jobs j
        LEFT JOIN applications a ON j.id=a.job_id
        GROUP BY j.id ORDER BY count DESC LIMIT 8
    """).fetchall()]
    by_category = [dict(r) for r in c.execute("SELECT category, COUNT(*) as count FROM jobs GROUP BY category").fetchall()]
    recent = [dict(r) for r in c.execute("""
        SELECT a.id, u.name as applicant, j.title as job, j.company, a.status, a.applied_at
        FROM applications a JOIN users u ON a.user_id=u.id JOIN jobs j ON a.job_id=j.id
        ORDER BY a.applied_at DESC LIMIT 5
    """).fetchall()]
    conn.close()
    return jsonify(totalJobs=total_jobs, activeJobs=active_jobs, totalUsers=total_users,
                   totalApplications=total_apps, appsPerJob=apps_per_job,
                   jobsByCategory=by_category, recentApps=recent)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db(); c = conn.cursor()
    search = request.args.get('search','')
    category = request.args.get('category','all')
    status = request.args.get('status','all')
    q = """SELECT j.*, u.name as posted_by_name,
           (SELECT COUNT(*) FROM applications WHERE job_id=j.id) as application_count
           FROM jobs j LEFT JOIN users u ON j.posted_by=u.id WHERE 1=1"""
    params = []
    if search: q += " AND (j.title LIKE ? OR j.company LIKE ?)"; params += [f'%{search}%','%'+search+'%']
    if category != 'all': q += " AND j.category=?"; params.append(category)
    if status != 'all': q += " AND j.status=?"; params.append(status)
    q += " ORDER BY j.created_at DESC"
    rows = [dict(r) for r in c.execute(q, params).fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    d = request.json
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO jobs (title,company,category,location,type,status,salary,posted_by) VALUES (?,?,?,?,?,?,?,1)',
              (d['title'],d['company'],d['category'],d['location'],d.get('type','Full-time'),d.get('status','active'),d.get('salary','')))
    conn.commit(); conn.close()
    return jsonify(message='Job created')

@app.route('/api/jobs/<int:jid>', methods=['DELETE'])
def delete_job(jid):
    conn = get_db(); c = conn.cursor()
    c.execute('DELETE FROM applications WHERE job_id=?', (jid,))
    c.execute('DELETE FROM jobs WHERE id=?', (jid,))
    conn.commit(); conn.close()
    return jsonify(message='Job deleted')

@app.route('/api/jobs/<int:jid>', methods=['PATCH'])
def update_job(jid):
    d = request.json
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE jobs SET status=? WHERE id=?', (d['status'],jid))
    conn.commit(); conn.close()
    return jsonify(message='Job updated')

@app.route('/api/applications')
def get_apps():
    conn = get_db(); c = conn.cursor()
    search = request.args.get('search','')
    q = """SELECT a.id, u.name as applicant, u.email, j.title as job, j.company, j.category,
           a.status, a.applied_at FROM applications a
           JOIN users u ON a.user_id=u.id JOIN jobs j ON a.job_id=j.id WHERE 1=1"""
    params = []
    if search: q += " AND (u.name LIKE ? OR j.title LIKE ?)"; params += [f'%{search}%',f'%{search}%']
    q += " ORDER BY a.applied_at DESC"
    rows = [dict(r) for r in c.execute(q, params).fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/applications/<int:aid>', methods=['DELETE'])
def delete_app(aid):
    conn = get_db(); c = conn.cursor()
    c.execute('DELETE FROM applications WHERE id=?', (aid,))
    conn.commit(); conn.close()
    return jsonify(message='Deleted')

@app.route('/api/applications/<int:aid>', methods=['PATCH'])
def update_app(aid):
    d = request.json
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE applications SET status=? WHERE id=?', (d['status'],aid))
    conn.commit(); conn.close()
    return jsonify(message='Updated')

@app.route('/api/users')
def get_users():
    conn = get_db(); c = conn.cursor()
    rows = [dict(r) for r in c.execute("""
        SELECT u.*, COUNT(a.id) as applications_count FROM users u
        LEFT JOIN applications a ON u.id=a.user_id GROUP BY u.id ORDER BY u.created_at DESC
    """).fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    conn = get_db(); c = conn.cursor()
    c.execute('DELETE FROM applications WHERE user_id=?', (uid,))
    c.execute('DELETE FROM users WHERE id=?', (uid,))
    conn.commit(); conn.close()
    return jsonify(message='Deleted')

@app.route('/api/categories')
def get_categories():
    conn = get_db(); c = conn.cursor()
    rows = [r[0] for r in c.execute('SELECT DISTINCT category FROM jobs ORDER BY category').fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    @app.route('/')
def home():
    return jsonify(message='Job Portal API is running!')
    init_db()
    print("🚀 Server running at http://localhost:5000")
    app.run(port=5000, debug=True)
