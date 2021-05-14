import datetime
import json
import os
import mysql.connector
import datetime
from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from posts import Posts
from werkzeug import secure_filename

import pymysql
pymysql.install_as_MySQLdb()

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="pythondb"
)

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'ks'
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://root:@localhost/pythondb'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = params['upload_location']


@app.route("/")
def index():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template("index.html",params=params,posts=posts)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post)



@app.route("/registration")
def registration():
    return render_template("registration.html")


@app.route("/registration_post", methods=["post"])
def registration_post():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    a = request.form.get("k1")
    b = request.form.get("k2")
    c = request.form.get("k3")
    d = request.form.get("k4")
    e = request.form.get("k5")
    mycursor.execute("insert into registration values('" + a + "','" + b + "','" + c + "','" + d + "','" + e + "')")
    mycursor.execute("insert into login values('" + a + "','" + b + "')")
    mydb.commit()
    return render_template("login.html", data="registerd successfull")




@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_post", methods=["post"])
def login_post():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )

    mycursor = mydb.cursor()
    a = request.form.get("k1")
    b = request.form.get("k2")
    mycursor.execute("select * from login where loginid='" + a + "' and password='" + b + "'")

    records = mycursor.fetchall()

    flag = 0
    for row in records:
        flag = 1

    if flag == 1:
        session['loginid'] = a
        return render_template('profile.html', data=a)

    else:
        return render_template('registration.html', data="invalid user name or password")



@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):

        if request.method =="POST":
            title = request.form.get('k1')
            slug = request.form.get('k2')
            content = request.form.get('k3')
            date = datetime.datetime.now()

            if sno == '0':
                post =Posts (title=title,slug=slug,content=content,date=date)
                db.session.add(post)
                db.session.commit()


            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title=title
                post.slug = slug
                post.content = content
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()


        if post is None:
            sno=0


        return render_template('edit.html', post=post,sno=sno)


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/profile_post", methods=["POST"])
def profile_post():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )

    posts = Posts.query.all()

    return render_template("admin.html", posts=posts)


@app.route("/chngpwrd")
def chngpwrd():
    return render_template("chngpwrd.html")


@app.route("/changepaswrd_post", methods=["post"])
def chngpwrd_post():
    a = request.form.get("op")
    b = request.form.get("np")
    c = request.form.get("cp")
    loginid = session["loginid"]
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("select passwrd from login where loginid='" + loginid + "'")
    records = mycursor.fetchall()
    dbpwd = ""
    for row in records:
        dbpwd = row[0]
    if (dbpwd == a):
        if (b == c):
            mycursor.execute("update login set passwrd='" + c + "' where loginid='" + loginid + "' ")
            mydb.commit()
            return render_template("chngpwrd.html", data="password update successfull", loginid=sender)
        else:
            return render_template("chngpwrd.html", data="password not match", loginid=sender)
    else:
        return render_template("chngpwrd.html", data="old password not match", loginid=sender)


@app.route("/compose")
def compose():
    return render_template("compose.html")


@app.route("/compose_post", methods=["post"])
def compose_post():
    a = request.form.get("no")
    b = request.form.get("dt")
    c = request.form.get("rev")
    d = request.form.get("msg")
    sender = session["loginid"]
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("insert into compose values ('" + a + "','" + b + "','" + sender + "','" + d + "')")
    mydb.commit()
    return render_template("compose.html", data="msg send succesfully...", loginid=sender)


@app.route("/inbox")
def inbox():
    sender = session["loginid"]
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("select * from compose where name ='" + sender + "'")
    records = mycursor.fetchall()
    return render_template("inbox.html", data=records, loginid=sender)


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/upload_post", methods=["post"])
def upload_post():
    if (request.method == "POST"):

        f = request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return "uploaded succesfully"

@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):
    post = Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return "post deleted succesfully"

@app.route("/logout")
def logout():
    session.pop("loginid")
    return redirect("/index")













@app.route("/css")
def css():
    return render_template("css.html")


@app.route("/back_img")
def back_img():
    return render_template("back_img.html")


@app.route("/sendvalue")
def sendvalue():
    return render_template("sendvalue.html", name="kunal")


@app.route("/sendvalue_input")
def sendvalue_input():
    return render_template("sendvalue_input.html")


@app.route("/sendvalue_input", methods=["post"])
def sendvalue_input_post():
    a = request.form.get("t1")
    return render_template("sendvalue_input.html", name=a)


@app.route("/full_name")
def full_name():
    return render_template("full_name.html")


@app.route("/full_name", methods=["post"])
def full_name_post():
    a = request.form.get("n1")
    b = request.form.get("n2")
    return render_template("full_name.html", name_1=a, name_2=b)


@app.route("/product")
def product():
    return render_template("product.html")


@app.route("/product_post", methods=["post"])
def product_post():
    a = request.form.get("p1")
    price = 0
    if (a == "car"):
        price = 500000
    elif (a == "bike"):
        price = 100000
    elif (a == "cycle"):
        price = 10000

    return render_template("product.html", name=price)


@app.route("/add")
def add():
    return render_template("add.html")


@app.route("/add", methods=["post"])
def add_post():
    sum = 0
    a = request.form.get("n1")
    b = request.form.get("n2")
    sum = int(a) + int(b)
    return render_template("add.html", x=sum)


@app.route("/dbinsert")
def dbinsert():
    return render_template("dbinsert.html")


@app.route("/dbinsert_post", methods=["post"])
def dbinsert_post():
    a = request.form.get("e1")
    b = request.form.get("e2")
    c = request.form.get("e3")

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("insert into emp values (" + a + ",'" + b + "'," + c + ")")
    mydb.commit()
    return render_template("dbinsert.html", data="record added")


@app.route("/dbupdate")
def dbupdate():
    return render_template("dbupdate.html")


@app.route("/dbupdate_post", methods=["post"])
def dbupdate_post():
    a = request.form.get("e1")
    b = request.form.get("e2")
    c = request.form.get("e3")

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("update emp set name='" + b + "',sal=" + c + " where id=" + a + "")
    mydb.commit()
    return render_template("dbupdate.html", data="record updated")


@app.route("/dbselect")
def dbselect():
    return render_template("dbselect.html")


@app.route("/dbselect_post", methods=["post"])
def dbselect_post():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="pythondb"
    )
    mycursor = mydb.cursor()
    a = request.form.get("e1")
    mycursor.execute("select * from emp where id=" + a + "")
    records = mycursor.fetchall()
    ename = ""
    sal = ""
    for row in records:
        name = row[1]
        sal = row[2]
    data = [name, sal]
    return render_template("dbselect.html", rec=data)



app.run(debug=True)
