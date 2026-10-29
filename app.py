from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Session security key
app.secret_key = "fitzone-project-secret-key"


# DATABASE CONNECTION
def get_db():

    connection = sqlite3.connect("gym.db")

    connection.row_factory = sqlite3.Row

    return connection


# CREATE DATABASE
def create_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS members (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            phone TEXT NOT NULL,

            password TEXT NOT NULL,

            plan TEXT NOT NULL

        )
    """)

    connection.commit()
    connection.close()


create_database()


# HOME
@app.route("/")
def home():

    return render_template("index.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        phone = request.form["phone"].strip()

        password = request.form["password"]

        plan = request.form["plan"]


        hashed_password = generate_password_hash(password)


        try:

            connection = get_db()

            connection.execute(
                """
                INSERT INTO members
                (name, email, phone, password, plan)

                VALUES (?, ?, ?, ?, ?)
                """,

                (
                    name,
                    email,
                    phone,
                    hashed_password,
                    plan
                )
            )

            connection.commit()
            connection.close()


            return redirect(url_for("login"))


        except sqlite3.IntegrityError:

            return "This email is already registered!"


    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]


        connection = get_db()

        member = connection.execute(
            "SELECT * FROM members WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()


        if member and check_password_hash(
            member["password"],
            password
        ):

            session["member_id"] = member["id"]

            return redirect(url_for("dashboard"))


        return render_template(
            "login.html",
            error="Invalid email or password."
        )


    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "member_id" not in session:

        return redirect(url_for("login"))


    connection = get_db()

    member = connection.execute(
        "SELECT * FROM members WHERE id = ?",
        (session["member_id"],)
    ).fetchone()

    connection.close()


    if member is None:

        session.clear()

        return redirect(url_for("login"))


    return render_template(
        "dashboard.html",
        member=member
    )


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":

    app.run(debug=True)