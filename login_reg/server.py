from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key = "O koto kawaii"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# email validation - must follow standard email format
PW_REGEX = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}') 
# password validation - must ha

@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/submit-newuser", methods=["POST"])
def newuser():
    
    mysql = connectToMySQL("users")
    query = "SELECT email FROM users"
    all_emails = mysql.query_db(query)
    
    for email in all_emails:
        print("*"*30)
        print("looped once")
        print(email)
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

@app.route("/login", methods=["POST"])
def login():
    mysql = connectToMySQL("users")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data ={
        "email": request.form["email"]
    }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]["password_hash"], request.form["pw"]):
            session["userid"] = result[0]["id"]
        else:
            flash(u"You could not be logged in.", "error")
    else:
        flash(u"User does not exist.", "invalid")
    
    return redirect("/success")

@app.route("/success")
def success():
    if "userid" in session:
        mysql = connectToMySQL("users")
        query = "SELECT * FROM users WHERE id = %(id)s"
        data = {
            "id": session["userid"]
        }
        current_user = mysql.query_db(query, data)
        session["current_user"] = current_user[0]
    return render_template("success.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)