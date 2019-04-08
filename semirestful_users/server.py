from flask import Flask, render_template, request, redirect
from mysqlconnection import connectToMySQL

app = Flask(__name__)

@app.route("/users")
def index():
    mysql = connectToMySQL("users")
    users = mysql.query_db("SELECT CONCAT(first_name, ' ', last_name) as name, email, CONCAT(MONTHNAME(created_at), ' ', DAY(created_at), ', ', YEAR(created_at)) as date FROM users")
    return render_template("users.html", users_html = users)


@app.route("/add-user")
def add_user():
    
    return render_template("create.html")

@app.route("/users/<id>")
def view_user(id):
    
    return render_template("readone.html")

@app.route("users/<id>/edit")
def edit_user(id):
    
    return render_template("update.html")

@app.route("users/<id>/delete")
def remove_user(id):
    
    return redirect("/users")

if __name__ == "__main__":
    app.run(debug=True)