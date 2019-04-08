from flask import Flask, render_template, redirect, request
from mysqlconnection import connectToMySQL

app = Flask(__name__)

@app.route("/")
def index():
    mysql = connectToMySQL("pets")
    pets = mysql.query_db("SELECT * FROM pets")
    return render_template("index.html", pets_html = pets)

@app.route("/add-pet", methods=["POST"])
def add_pet():
    query = "INSERT INTO pets(name, type) VALUES (%(newpet_name)s, %(newpet_type)s)"
    data = {
        "newpet_name": request.form["name"],
        "newpet_type": request.form["type"]
    }
    mysql = connectToMySQL("pets")
    mysql.query_db(query,data)
    
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)