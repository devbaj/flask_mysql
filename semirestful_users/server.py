from flask import Flask, render_template, request, redirect
from mysqlconnection import connectToMySQL

app = Flask(__name__)

@app.route("/users") # SHOW ALL USERS - COMPLETE
def index():
    mysql = connectToMySQL("users")
    users = mysql.query_db("SELECT id, CONCAT(first_name, ' ', last_name) as name, email, CONCAT(MONTHNAME(created_at), ' ', DAY(created_at), ', ', YEAR(created_at)) as date FROM users")
    return render_template("users.html", users_html = users)
#

@app.route("/add-user") # ADD USER
def add_user():
    
    return render_template("create.html")

@app.route("/process-add-user", methods=["POST"]) # PROCESS ADD
def proc_adduser(id):
    
    return redirect(f"users/{id}") # redirect to newly created users's page

@app.route("/users/<id>") # SHOW USER - COMPLETE
def view_user(id):
    mysql = connectToMySQL("users")
    user = mysql.query_db(f"SELECT CONCAT(first_name, ' ', last_name) as name, email, CONCAT(MONTHNAME(created_at), ' ', DAY(created_at), ', ', YEAR(created_at)) as creation_date, CONCAT(MONTHNAME(updated_at), ' ', DAY(updated_at), ', ', YEAR(updated_at), ' at ', DATE_FORMAT(updated_at, '%r' )) as last_update FROM users WHERE id = {id}")
    print("*"*30)
    print(user)
    print("*"*30)
    return render_template("readone.html", id_html = id, user_html = user[0])
    
@app.route("/users/<id>/edit")
def edit_user(id):
    
    return render_template("update.html")

@app.route("/process-edit-user", methods=["POST"])
def proc_edituser(id):
    
    return redirect(f"users/{id}")

@app.route("/users/<id>/delete")
def remove_user(id):
    
    return redirect("/users")

if __name__ == "__main__":
    app.run(debug=True)