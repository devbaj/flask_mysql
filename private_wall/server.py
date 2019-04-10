from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = "Hanabi..."
bcrypt = Bcrypt(app)

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/process-registration", methods=["POST"])
def register():
    mysql = connectToMySQL("users") # change to schema name
    query = "SELECT email FROM users"
    all_emails = mysql.query_db(query)
    
    for email in all_emails:
        if email["email"] == request.form["email"]:
            flash(u"Email address has already been used.", "error")
    
    if len(request.form["fname"]) < 1:
        flash(u"First name cannot be blank!", "blank")
    if len(request.form["lname"]) < 1:
        flash(u"Last name cannot be blank!", "blank")

    if not EMAIL_REGEX.match(request.form["email"]):
        flash(u"Invalid email address!", "invalid")
    elif not PW_REGEX.match(request.form["pw"]):
        flash(u"Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase character, and one number.", "invalid")
    elif request.form["pw"] != request.form["pw_confirm"]:
        flash(u"Passwords do not match.", "error")
    elif not "_flashes" in session.keys():
        pw_hash = bcrypt.generate_password_hash(request.form["pw"])
        mysql = connectToMySQL("users")
        query = "INSERT INTO users(first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(pwhash)s, NOW(), NOW())"
        data = {
            "fname": request.form["fname"],
            "lname": request.form["lname"],
            "email": request.form["email"],
            "pwhash": pw_hash,
        }
        mysql.query_db(query, data)
        flash(u"User registered successfully!", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)