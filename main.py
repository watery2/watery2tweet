from datetime import datetime
from flask import Flask, session, redirect, url_for, render_template, request, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import random


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

class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),unique=False,nullable=False)
    friends = db.Column(db.String,unique=False,nullable=False)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),unique=False,nullable=False)
    post = db.Column(db.String,unique=False,nullable=False)

class MyModelView(ModelView):
    def is_accessible(self):
        if "name" in session:
            name = session["name"]
            if name == "***":
                return True
            else:
                return False
        else:
            False
    def inaccessible_callback(self, name, **kwargs):
        return False

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if "name" in session:
            name = session["name"]
            if name == "***":
                return True
            else:
                return False
        else:
            False
    def inaccessible_callback(self, name, **kwargs):
        return False

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Friends, db.session))
admin.add_view(MyModelView(Posts, db.session))

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
                            add_user = User(name=name, password=password, desc=" ")
                            db.session.add(add_user)
                            db.session.commit() 
                            return redirect(url_for("login"))
                        except IntegrityError:
                            flash("Password or Username is being used")
        else:
            flash("Enter Something")
    return render_template("register.html")

@app.route("/login")
def login_redirect():
    return redirect(url_for("login"))

# The profile is named home cause i'm in too deep to change it 
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
                friends_user = Friends.query.filter_by(name=usr).all()
                you_as_a_friend = Friends.query.filter_by(friends=usr).all()
                friends_list = []
                people_who_friended_you = []
                try:
                    for i in friends_user:
                        friends_list.append(i.friends)
                except AttributeError:
                    pass
                try:
                    for i in you_as_a_friend:
                        people_who_friended_you.append(i.name)
                except AttributeError:
                    pass
                try:
                    for i in people_who_friended_you:
                        if i in friends_list:
                            people_who_friended_you.remove(i)
                except AttributeError:
                    pass
                if request.method == "POST":
                    description = request.form["desc_text"]
                    user.desc = description
                    db.session.commit()
                    return redirect(url_for("home", usr=name))
                user_posts = Posts.query.filter_by(name=user_name).all()
                user_posts_list = []
                try:
                    for i in user_posts:
                        user_posts_list.append(i.post)
                except AttributeError:
                    pass
                return render_template("profile_user.html", name=name, view_name=view_name, desc=descrip, friend=friends_list, pfriend=people_who_friended_you, posts=user_posts_list)
            else:
                friend_or_unfriend = ""
                view_user_friends = Friends.query.filter_by(name=view_name).all()
                view_friends_list = []
                try:
                    for i in view_user_friends:
                        view_friends_list.append(i.friends)
                except AttributeError:
                    pass
                friends_user = Friends.query.filter_by(name=usr).all()
                friends_list = []
                try:
                    for i in friends_user:
                        friends_list.append(i.friends)
                except AttributeError:
                    pass
                if usr in view_friends_list:
                    friend_or_unfriend = "Unfriend"
                else:
                    friend_or_unfriend = "Friend"
                if request.method == "POST":
                    if usr not in view_friends_list:
                        new_friend = Friends(name=view_name, friends=usr)
                        db.session.add(new_friend)
                        db.session.commit()
                    else:
                        del_friend = Friends.query.filter_by(name=view_name, friends=usr).first()
                        db.session.delete(del_friend)
                        db.session.commit()
                    return redirect(url_for("home", usr=usr))
                user_posts = Posts.query.filter_by(name=user_name).all()
                user_posts_list = []
                try:
                    for i in user_posts:
                        user_posts_list.append(i.post)
                except AttributeError:
                    pass
                return render_template("profile_view.html", name=user_name, view_name=view_name, desc=descrip, friend=friends_list, friend_or=friend_or_unfriend, posts=user_posts_list)
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
@app.route("/home", methods=['GET', 'POST'])
def post():
    if "name" in session:
        name = session["name"]
        if request.method == "POST":
            post_words = request.form["post_text"]
            post_new = Posts(name=name, post=post_words)
            db.session.add(post_new)
            db.session.commit()
            return redirect(url_for("post"))
        
        posts_all = Posts.query.all()
        names_list = []
        posts_list = []
        try:
            for i in posts_all:
                names_list.append(i.name)
                posts_list.append(i.post)
        except AttributeError:
            pass
        
        zip_list = list(zip(names_list,posts_list))
        random.shuffle(zip_list)
        try:
            names_list, posts_list = zip(*zip_list)
        except ValueError:
            pass

        if len(names_list) > 200 and len(posts_list) > 200:
            names_list = names_list[0:201]
            posts_list = posts_list[0:201]
        lens = len(names_list)
        names_and_posts = zip(names_list, posts_list)
        return render_template("home.html", view_name=name,info=names_and_posts)
    else:
        return redirect(url_for("login"))
   
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)