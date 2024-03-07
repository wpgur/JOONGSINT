from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
from datetime import timedelta
import pymysql
import os
 
mysql_host = os.environ.get('MYSQL_HOST', '127.0.0.1')
mysql_port= int(os.environ.get('MYSQL_PORT', 3308))
mysql_user =  os.environ.get('MYSQL_USER', 'root')
mysql_password = os.environ.get('MYSQL_PASSWORD', '')
mysql_db = os.environ.get('MYSQL_DB', 'joongsint')

login_module = Blueprint("login_module", __name__)

@login_module.route("/login", methods=['GET', 'POST'])
def login_result():
    if request.method == 'POST':
        error = None

        db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

        id = request.form['id']
        pw = request.form['pw']

        cursor = db.cursor()

        sql = "SELECT id FROM user WHERE id = %s AND pw = %s"
        value = (id, pw)

        cursor.execute(sql, value)

        data = cursor.fetchone()
        db.commit()
        db.close()

        if data:
            session['login_user'] = data[0]
            # app.permanent_session_lifetime = timedelta(days=1)
            # 세션 유지
            session.permanent = True
            return render_template("index.html", user_id=data[0])
        else:
            error = 'invalid input data detected !'
            return render_template("error.html", error=error)
        
    return render_template("login.html")

@login_module.route("/logout", methods=['GET'])
def logout():
    session.pop('login_user', None)
    return render_template("index.html")