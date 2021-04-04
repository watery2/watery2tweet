from datetime import datetime
from flask import Flask, session, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.main'
app.secret_key = "ngxz85"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),unique=True,nullable=False)
    password = db.Column(db.String(80),unique=True,nullable=False)
    desc = db.Column(db.String,nullable=False)
    friends = db.Column(db.PickleType, nullable=False)

@app.route("/",methods=['GET', 'POST'])
def login():
    if "name" in session:
        usr_name = session["name"]
        return redirect(url_for("home", usr=usr_name))
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        user = User.query.filter_by(name=name).first()
        try:
            if name == user.name and password == user.password:
                session["name"] = name
                session["password"] = password
                return redirect(url_for("home", usr=name))
            else:
                flash("password or username is wrong")
        except AttributeError:
            flash("password or username is wrong")
        
    return render_template("login.html")
@app.route("/register", methods=['GET', 'POST'])
def register():
    from sqlalchemy.exc import IntegrityError
    if "name" in session:
        usr_name = session["name"]
        return redirect(url_for("home", usr=usr_name))
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        user = User.query.filter_by(name=name).first()
        if name != "" and password != "":
            if "`" in name or '`' in password or "'" in name or "'" in password or "\"" in name or "\"" in password:
                flash("ERROR")
            else:
                try:
                    if name == user.name:
                        flash("Password or Username is being used")
                except AttributeError:
                    try:
                        if password == user.password:
                            flash("Password or Username is being used")
                    except AttributeError:  
                #else:
                        try:
                            add_user = User(name=name, password=password, desc=" ",friends=[])
                            db.session.add(add_user)
                            db.session.commit()
                            session["name"] = name
                            session["password"] = password
                            return redirect(url_for("home", usr=name))
                        except IntegrityError:
                            flash("Password or Username is being used")
        else:
            flash("Enter Something")
    return render_template("register.html")

@app.route("/login")
def login_redirect():
    return redirect(url_for("login"))

@app.route("/profile/<usr>", methods=['GET', 'POST'])
def home(usr):
    if "name" in session:
        view_name = session["name"]
        try:
            user = User.query.filter_by(name=usr).first()
            user_name = user.name
            descrip = user.desc
            if view_name == user_name:
                name = session["name"]
                if request.method == "POST":
                    description = request.form["desc_text"]
                    user.desc = description
                    db.session.commit()
                    return redirect(url_for("home", usr=name))
                return render_template("profile_user.html", name=name, view_name=view_name, desc=descrip)
            else:
                return render_template("profile_view.html", name=user_name, view_name=view_name, desc=descrip)
        except AttributeError:
            return render_template("404.html")
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "name" in session:
        session.pop("name", None)
        session.pop("password", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))
@app.route("/test")
def test():
    users = User.query.all()
    names = []
    for user in users:
        names.append(user.name)
    return render_template("test.html", names=names)    
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)