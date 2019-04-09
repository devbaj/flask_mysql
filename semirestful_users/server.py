from flask import Flask, render_template, request, redirect
from mysqlconnection import connectToMySQL
from datetime import datetime

app = Flask(__name__)

@app.route("/users") # SHOW ALL USERS - COMPLETE
def index():
    mysql = connectToMySQL("users")
    users = mysql.query_db("SELECT id, CONCAT(first_name, ' ', last_name) as name, email, CONCAT(MONTHNAME(created_at), ' ', DAY(created_at), ', ', YEAR(created_at)) as date FROM users")
    return render_template("users.html", users_html = users)
#

@app.route("/users/new") # ADD USER FORM - COMPLETE
def add_user():
    return render_template("create.html")


@app.route("/process-add-user", methods=["POST"]) # PROCESS ADD - COMPLETE
def proc_adduser():
    query = "INSERT INTO users(first_name, last_name, email, created_at, updated_at) VALUES (%(new_fname)s, %(new_lname)s, %(new_email)s, NOW(), NOW())"
    data = {
        "new_fname": request.form["fname"],
        "new_lname": request.form["lname"],
        "new_email": request.form["email"],
    }
    mysql = connectToMySQL("users")
    id = mysql.query_db(query, data)
    
    return redirect(f"users/{id}") # redirect to newly created users's page


@app.route("/users/<id>") # SHOW USER - COMPLETE
def view_user(id):
    query = "SELECT CONCAT(first_name, ' ', last_name) as name, email, CONCAT(MONTHNAME(created_at), ' ', DAY(created_at), ', ', YEAR(created_at)) as creation_date, updated_at FROM users WHERE id = %(id)s;"
    data = {
        "id": id
    }
    mysql = connectToMySQL("users")
    user = mysql.query_db(query, data)
    updated_at = user[0]["updated_at"]
    update_date = datetime.strftime(updated_at, '%B %d, %Y at %I:%M:%S %p')
    return render_template("readone.html", id_html = id, user_html = user[0], html_update = update_date)


@app.route("/users/<id>/edit") # USER EDIT FORM - COMPLETE
def edit_user(id):
    mysql = connectToMySQL("users")
    query = "SELECT first_name, last_name, email FROM users WHERE id = %(id)s"
    data = {
        "id": id
    }
    user = mysql.query_db(query, data)
    return render_template("update.html", id_html = id, user_html = user[0])


@app.route("/process-edit-user/<id>", methods=["POST"]) # USER UPDATE POST - COMPLETE
def proc_edituser(id):
    query = "UPDATE users SET first_name = %(new_fname)s, last_name = %(new_lname)s, email = %(new_email)s, updated_at = NOW() WHERE id = %(id)s"
    data = {
        "new_fname": request.form["fname"],
        "new_lname": request.form["lname"],
        "new_email": request.form["email"],
        "id": id
    }
    mysql = connectToMySQL("users")
    mysql.query_db(query, data)
    return redirect(f"/users/{id}")

@app.route("/users/<id>/delete")
def remove_user(id):
    mysql = connectToMySQL("users")
    query = "DELETE FROM users WHERE id = %(id)s"
    data = {
        "id": id
    }
    mysql.query_db(query, data)
    return redirect("/users")

if __name__ == "__main__":
    app.run(debug=True)