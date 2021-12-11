import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///bloodline.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return render_template("register.html", u = 0)

        # Ensure password was submitted
        if not password:
            return render_template("register.html", p = 0)

        # Ensures that password confirmation is the same as the password
        if not password == confirmation:
            return render_template("register.html", c = 0)

        # Checks if the username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?;", username)

        if len(rows) == 1:
            return render_template("register.html", u = 1)


        db.execute("INSERT INTO users(username, hash) VALUES(?, ?);", request.form.get(
                   "username"), generate_password_hash(request.form.get("password")))

        row = db.execute("SELECT * FROM users WHERE username = ?;", username)

        # Logs the user in
        session["user_id"] = row[0]["id"]

        # Redirect user to login page
        return redirect("/")

    # User reached route via GET(as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", u = 0)


        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", p = 0)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", c = 0)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Adds a member to the tree"""

    if request.method == "POST":

        fname = request.form.get("fname")
        lname = request.form.get("lname")
        gender = request.form.get("gender")
        fparent1 = request.form.get("fparent1")
        lparent1 = request.form.get("lparent1")
        fparent2 = request.form.get("fparent2")
        lparent2 = request.form.get("lparent2")

        if not fname:
            return render_template("add.html", f = 0)

        if not lname:
            return render_template("add.html", l = 0)

        if not gender:
            return render_template("add.html", g = 0)

        db.execute("INSERT INTO test(name, gender) VALUES(?,?);", fname + " " + lname, gender)

        return redirect("/")
    else:
        return render_template("add.html")

@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():

    if request.method == "POST":

        fname = request.form.get("fname")
        lname = request.form.get("lname")

        if not fname:
            return render_template("remove.html", f = 0)

        if not lname:
            return render_template("remove.html", l = 0)

        return redirect("/")

    else:
        return render_template("remove.html")