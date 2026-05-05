from flask import Flask, request, redirect, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

ADMIN = {
    "username": "1234",
    "password": "1234"
}

app = Flask(__name__)
app.secret_key = "pahintulot_secret"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("pahintulot.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        approved INTEGER DEFAULT 0
    )
    """)

    # POSTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# page route
@app.route("/feed")
def feed():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("pahintulot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()

    return render_template_string(FEED_PAGE, posts=posts, user=session["user"])

@app.route("/post", methods=["POST"])
def post():
    if "user" not in session:
        return redirect("/")

    content = request.form["content"]

    conn = sqlite3.connect("pahintulot.db")
    c = conn.cursor()

    c.execute("INSERT INTO posts (username, content) VALUES (?, ?)",
              (session["user"], content))

    conn.commit()
    conn.close()

    return redirect("/feed")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN["username"] and password == ADMIN["password"]:
            session["admin"] = True
            return redirect("/admin")
        else:
            msg = "Wrong admin credentials"

    return render_template_string(ADMIN_LOGIN, msg=msg)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")

    conn = sqlite3.connect("pahintulot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    return render_template_string(ADMIN_PAGE, users=users)

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin-login")


# ---------------- PAGES ----------------

FEED_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PAHINTULOT Feed</title>
    <style>
        body {
            font-family: Arial;
            background: #f4f7fb;
            margin: 0;
        }

        .topbar {
            background: #1877f2;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
        }

        .container {
            width: 600px;
            margin: 20px auto;
        }

        .post-box {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        textarea {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }

        button {
            margin-top: 8px;
            padding: 10px;
            width: 100%;
            background: #1877f2;
            color: white;
            border: none;
            border-radius: 8px;
        }

        .feed-post {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }

        .user {
            font-weight: bold;
            color: #1877f2;
        }

        .time {
            font-size: 11px;
            color: gray;
        }
    </style>
</head>
<body>

<div class="topbar">
    <div>PAHINTULOT Feed</div>
    <div>{{user}}</div>
</div>

<div class="container">

    <div class="post-box">
        <form method="POST" action="/post">
            <textarea name="content" placeholder="What do you feel today?" required></textarea>
            <button type="submit">Post</button>
        </form>
    </div>

    {% for p in posts %}
    <div class="feed-post">
        <div class="user">{{p[1]}}</div>
        <div class="time">{{p[3]}}</div>
        <p>{{p[2]}}</p>
    </div>
    {% endfor %}

</div>

</body>
</html>
"""


LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PAHINTULOT Login</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #1877f2, #42a5f5, #e3f2fd);
        }

        .container {
            display: flex;
            gap: 50px;
            align-items: center;
        }

        .left {
            color: white;
        }

        .left h1 {
            font-size: 60px;
            margin: 0;
            letter-spacing: 2px;
        }

        .left p {
            font-size: 18px;
            opacity: 0.9;
            max-width: 300px;
        }

        .card {
            width: 340px;
            padding: 25px;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }

        .card h2 {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 8px;
            outline: none;
        }

        input:focus {
            transform: scale(1.02);
            transition: 0.2s;
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: none;
            border-radius: 8px;
            background: #0d47a1;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #08306b;
            transform: scale(1.05);
        }

        .error {
            color: #ffdddd;
            text-align: center;
            margin-top: 10px;
        }

        .link {
            text-align: center;
            margin-top: 15px;
        }

        .link a {
            color: white;
            text-decoration: none;
        }

        .link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="left">
        <h1>PAHINTULOT</h1>
        <p>Secure access system. Only approved users can enter the platform.</p>
    </div>

    <div class="card">
        <h2>Login</h2>

        <form method="POST">
            <input type="text" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>

        {% if msg %}
        <div class="error">{{ msg }}</div>
        {% endif %}

        <div class="link">
            <a href="/register">Create new account</a>
        </div>
    </div>

</div>

</body>
</html>
"""
REGISTER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PAHINTULOT Register</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #42a5f5, #1e88e5, #bbdefb);
        }

        .container {
            display: flex;
            gap: 50px;
            align-items: center;
        }

        .left {
            color: white;
        }

        .left h1 {
            font-size: 55px;
            margin: 0;
        }

        .left p {
            font-size: 18px;
            max-width: 300px;
            opacity: 0.9;
        }

        .card {
            width: 340px;
            padding: 25px;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }

        .card h2 {
            text-align: center;
            color: white;
            margin-bottom: 15px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 8px;
            outline: none;
        }

        input:focus {
            transform: scale(1.02);
            transition: 0.2s;
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: none;
            border-radius: 8px;
            background: #0d47a1;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #08306b;
            transform: scale(1.05);
        }

        .msg {
            text-align: center;
            color: white;
            margin-top: 10px;
        }

        .link {
            text-align: center;
            margin-top: 15px;
        }

        .link a {
            color: white;
            text-decoration: none;
        }

        .link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="left">
        <h1>JOIN PAHINTULOT</h1>
        <p>Create your account and wait for owner approval before accessing the system.</p>
    </div>

    <div class="card">
        <h2>Register</h2>

        <form method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="text" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Submit</button>
        </form>

        {% if msg %}
        <div class="msg">{{ msg }}</div>
        {% endif %}

        <div class="link">
            <a href="/">Back to Login</a>
        </div>
    </div>

</div>

</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PAHINTULOT Admin Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            box-sizing: border-box;
        }

        body {
            background: #f4f7fb;
            display: flex;
        }

        /* SIDEBAR */
        .sidebar {
            width: 240px;
            height: 100vh;
            background: #111827;
            color: white;
            padding: 20px;
        }

        .sidebar h2 {
            color: #60a5fa;
            margin-bottom: 20px;
        }

        .sidebar a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            transition: 0.2s;
        }

        .sidebar a:hover {
            background: #1f2937;
        }

        /* MAIN */
        .main {
            flex: 1;
            padding: 20px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .topbar h1 {
            color: #111827;
        }

        .badge {
            background: #dbeafe;
            color: #1d4ed8;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
        }

        /* STATS CARDS */
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .card {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }

        .card h3 {
            color: #111827;
            margin-bottom: 5px;
        }

        /* USER LIST */
        .table {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }

        .user {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #eee;
        }

        .user:last-child {
            border-bottom: none;
        }

        .info {
            display: flex;
            flex-direction: column;
        }

        .name {
            font-weight: bold;
            color: #111827;
        }

        .email {
            font-size: 12px;
            color: gray;
        }

        /* STATUS */
        .status {
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 20px;
            margin-right: 10px;
        }

        .pending {
            background: #fef3c7;
            color: #92400e;
        }

        .approved {
            background: #dcfce7;
            color: #166534;
        }

        /* BUTTONS */
        .btn {
            padding: 6px 10px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
        }

        .approve {
            background: #22c55e;
            color: white;
        }

        .approve:hover {
            background: #16a34a;
        }

    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <h2>PAHINTULOT</h2>
        <a href="/admin">Dashboard</a>
        <a href="#">Users</a>
        <a href="#">Settings</a>
        <a href="/admin-logout">Logout</a>
    </div>

    <!-- MAIN -->
    <div class="main">

        <!-- TOP BAR -->
        <div class="topbar">
            <h1>Admin Dashboard</h1>
            <div class="badge">OWNER PANEL</div>
        </div>

        <!-- STATS -->
        <div class="cards">
            <div class="card">
                <h3>Total Users</h3>
                <p>{{users|length}}</p>
            </div>

            <div class="card">
                <h3>Pending</h3>
                <p>
                    {{ users | selectattr(4, "equalto", 0) | list | length }}
                </p>
            </div>

            <div class="card">
                <h3>System</h3>
                <p>PAHINTULOT v1.0</p>
            </div>
        </div>

        <!-- USERS -->
        <div class="table">
            <h3 style="margin-bottom:10px;">User Requests</h3>

            {% for u in users %}
            <div class="user">

                <div class="info">
                    <div class="name">{{u[1]}}</div>
                    <div class="email">{{u[2]}}</div>
                </div>

                <div style="display:flex;align-items:center;">
                    
                    {% if u[4] == 0 %}
                        <span class="status pending">PENDING</span>
                        <a class="btn approve" href="/approve/{{u[0]}}">Approve</a>
                    {% else %}
                        <span class="status approved">APPROVED</span>
                    {% endif %}

                </div>

            </div>
            {% endfor %}

        </div>

    </div>

</body>
</html>
"""
ADMIN_LOGIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - PAHINTULOT</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            box-sizing: border-box;
        }

        body {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #0f172a, #1e3a8a, #2563eb);
        }

        .card {
            width: 360px;
            padding: 30px;
            border-radius: 16px;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            color: white;
            text-align: center;
        }

        .title {
            font-size: 26px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 13px;
            opacity: 0.8;
            margin-bottom: 20px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 10px;
            outline: none;
            font-size: 14px;
        }

        input:focus {
            transform: scale(1.02);
            transition: 0.2s;
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border: none;
            border-radius: 10px;
            background: #22c55e;
            color: white;
            font-size: 15px;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #16a34a;
            transform: scale(1.03);
        }

        .error {
            margin-top: 10px;
            color: #f87171;
            font-size: 13px;
        }

        .footer {
            margin-top: 15px;
            font-size: 12px;
            opacity: 0.7;
        }
    </style>
</head>

<body>

<div class="card">

    <div class="title">PAHINTULOT</div>
    <div class="subtitle">Admin Access Panel</div>

    <form method="POST">
        <input name="username" placeholder="Admin Username" required>
        <input name="password" type="password" placeholder="Admin Password" required>
        <button type="submit">Login</button>
    </form>

    {% if msg %}
        <div class="error">{{ msg }}</div>
    {% endif %}

    <div class="footer">
        Secure system access required
    </div>

</div>

</body>
</html>
"""

DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>PAHINTULOT Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            background: #f4f7fb;
            display: flex;
        }

        /* SIDEBAR */
        .sidebar {
            width: 240px;
            height: 100vh;
            background: #1877f2;
            color: white;
            padding: 20px;
        }

        .sidebar h2 {
            margin-bottom: 30px;
            font-size: 22px;
        }

        .nav {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .nav a {
            color: white;
            text-decoration: none;
            padding: 10px;
            border-radius: 8px;
            transition: 0.2s;
        }

        .nav a:hover {
            background: rgba(255,255,255,0.2);
        }

        /* MAIN */
        .main {
            flex: 1;
            padding: 25px;
        }

        /* TOP BAR */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .welcome {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }

        .logout {
            background: #ff4d4d;
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            text-decoration: none;
            transition: 0.2s;
        }

        .logout:hover {
            background: #e60000;
        }

        /* CARDS */
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }

        .card h3 {
            margin-bottom: 10px;
            color: #1877f2;
        }

        .status {
            padding: 5px 10px;
            border-radius: 20px;
            display: inline-block;
            font-size: 12px;
            margin-top: 10px;
        }

        .approved {
            background: #d4edda;
            color: #155724;
        }

        .pending {
            background: #fff3cd;
            color: #856404;
        }

        /* CONTENT BOX */
        .content {
            margin-top: 20px;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }

        .content h3 {
            margin-bottom: 10px;
        }

        .btn {
            margin-top: 10px;
            display: inline-block;
            padding: 10px 15px;
            background: #1877f2;
            color: white;
            border-radius: 8px;
            text-decoration: none;
        }

        .btn:hover {
            background: #125ecb;
        }

    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <h2>PAHINTULOT</h2>
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="#">Profile</a>
            <a href="#">Messages</a>
            <a href="#">Settings</a>
        </div>
    </div>

    <!-- MAIN -->
    <div class="main">

        <div class="topbar">
            <div class="welcome">Welcome, {{user}}</div>
            <a class="logout" href="/logout">Logout</a>
        </div>

        <!-- CARDS -->
        <div class="cards">
            <div class="card">
                <h3>Status</h3>
                <p>Your account is active</p>
                <div class="status approved">APPROVED</div>
            </div>

            <div class="card">
                <h3>Access Level</h3>
                <p>Standard User</p>
            </div>

            <div class="card">
                <h3>System</h3>
                <p>PAHINTULOT v1.0</p>
            </div>
        </div>

        <!-- CONTENT -->
        <div class="content">
            <h3>Access Granted</h3>
            <p>
                You have successfully entered the PAHINTULOT system.
                This platform is protected and requires owner permission.
            </p>

            <a class="btn" href="#">Enter Main Portal</a>
        </div>

    </div>

</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("pahintulot.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user:
            if user[4] == 0:
                msg = "Account not approved yet by owner."
            elif check_password_hash(user[3], password):
                session["user"] = user[1]
                return redirect("/feed")
            else:
                msg = "Wrong password"
        else:
            msg = "User not found"

    return render_template_string(LOGIN_PAGE, msg=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("pahintulot.db")
        c = conn.cursor()

        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                  (name, email, password))

        conn.commit()
        conn.close()

        msg = "Registered! Wait for owner approval."

        # optional redirect suggestion page
        return redirect("/")

    return render_template_string(REGISTER_PAGE, msg=msg)

@app.route("/approve/<int:user_id>")
def approve(user_id):
    conn = sqlite3.connect("pahintulot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET approved=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template_string(DASHBOARD, user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
