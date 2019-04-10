from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = "Hanabi..."
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PW_REGEX = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}') 

######################
# INDEX
######################
@app.route("/")
def index():
    
    if "userid" in session:
        mysql = connectToMySQL("private_wall")
        query = "SELECT first_name FROM users WHERE id = %(id)s;"
        data = {
            "id": session["userid"]
        }
        user = mysql.query_db(query, data)
        user_fname = user[0]["first_name"]
    else:
        user_fname = None
    
    return render_template("index.html", fname_html = user_fname)

######################
# USER REGISTRATION
######################
@app.route("/process-registration", methods=["POST"])
def register():
    mysql = connectToMySQL("private_wall") # change to schema name
    query = "SELECT email FROM private_wall.users"
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
        mysql = connectToMySQL("private_wall")
        query = "INSERT INTO users(first_name, last_name, email, pw_hash, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(pwhash)s, NOW(), NOW())"
        data = {
            "fname": request.form["fname"],
            "lname": request.form["lname"],
            "email": request.form["email"],
            "pwhash": pw_hash,
        }
        mysql.query_db(query, data)
        flash(u"User registered successfully!", "success")
    return redirect("/")

######################
# LOGIN
######################
@app.route("/login", methods=["POST"])
def login():
    mysql = connectToMySQL("private_wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data ={
        "email": request.form["email"]
    }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]["pw_hash"], request.form["pw"]):
            session["userid"] = result[0]["id"]
            id = session["userid"]
            print("*"*30)
            print(id)
            print("*"*30)
            return redirect(f"/user/{id}")
        else:
            flash(u"You could not be logged in.", "error")
    else:
        flash(u"User does not exist.", "invalid")
    return redirect("/")

######################
# LOGOUT
######################
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

######################
# DASHBOARD
######################
@app.route("/user/<id>")
def user_home(id):
    # QUERY CURRENT USER NAME TO DISPLAY WELCOME TEXT
    mysql = connectToMySQL("private_wall")
    query = "SELECT first_name FROM users WHERE id = %(id)s;"
    data = {
        "id": session["userid"]
    }
    user_fn = mysql.query_db(query, data)
    
    # QUERY LIST OF USERS TO DISPLAY CORRESPONDING SEND MESSAGE FORMS
    mysql2 = connectToMySQL("private_wall")
    query = "SELECT id as recipient_id, first_name, last_name FROM users WHERE id != %(id)s;"
    data = {
        "id": session["userid"]
    }
    users_list = mysql2.query_db(query, data)
    # print("*"*30)
    # print(users_list)
    # print("*"*30)
    
    # QUERY LIST OF MESSAGES WHERE CURRENT USER IS THE RECIPIENT
    mysql3 = connectToMySQL("private_wall")
    query = "SELECT * FROM messages WHERE recipient_id = %(id)s"
    data = {
        "id": session["userid"]
    }
    
    return render_template("userhome.html", fname_html = user_fn[0]["first_name"], users_list_html = users_list)

######################
# SEND MESSAGE
######################
@app.route("/send-message/<recipient_id>", methods=["POST"])
def send_msg(recipient_id):
    if len(request.form["msg-content"])  < 0:
        flash(u"Message is empty. Message was not sent.", "invalid")
    else:
        mysql = connectToMySQL("private_wall")
        query = "INSERT INTO messages(sender_id, recipient_id, content, created_at, updated_at) VALUES (%(sender_id)s, %(recipient_id)s, %(content)s, NOW(), NOW());"
        data= {
            "sender_id": session["userid"],
            "recipient_id": recipient_id,
            "content": request.form["msg-content"]
        }
        mysql.query_db(query, data)
        flash(u"Message sent!", "success")
    
    return redirect(f"/user/{session['userid']}")

if __name__ == "__main__":
    app.run(debug=True)