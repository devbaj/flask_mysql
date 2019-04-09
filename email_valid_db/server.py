from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = "So this is the power of Ultra Instinct?"


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route("/")
def index():
    
    
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    if not EMAIL_REGEX.match(request.form["email"]):
        flash("Invalid email address!")
        return redirect("/")
    else:
        
        mysql = connectToMySQL("emails")
        query = "INSERT INTO emails(address, created_at, updated_at) VALUES (%(email)s, NOW(), NOW());"
        data = {
            "email": request.form["email"]
        }
        session["id"] = mysql.query_db(query, data)
        
        return redirect("/success")

@app.route("/success")
def success():
    
    query = "SELECT address, created_at FROM emails"
    mysql = connectToMySQL("emails")
    emails = mysql.query_db(query)
    
    print("*"*30)
    print(emails)
    print("*"*30)
    # format creation time?
    
    return render_template("success.html", emails_html = emails, new_email_html = emails[int(session["id"])-1] )


if __name__ == "__main__":
    app.run(debug=True)