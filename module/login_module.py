from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
import pymysql
import os
 
mysql_host = os.environ.get('MYSQL_HOST', 'mysql')
mysql_port= int(os.environ.get('MYSQL_PORT', 3306))
mysql_user =  os.environ.get('MYSQL_USER', 'root')
mysql_password = os.environ.get('MYSQL_PASSWORD', 'password')
mysql_db = os.environ.get('MYSQL_DB', 'petclinic')

login_module = Blueprint("login_module", __name__)

@login_module.route("/login", methods=['GET', 'POST'])
def login_result():
    if request.method == 'POST':
        error = None

        db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

        id = request.form['id']
        pw = request.form['pw']

        cursor = db.cursor()

        sql = "SELECT id FROM login_table WHERE id = %s AND pw = %s"
        value = (id, pw)

        cursor.execute(sql, value)

        data = cursor.fetchone()
        db.commit()
        db.close()

        if data:
            session['login_user'] = data[0]
            return render_template("index.html", user_id=data[0])
        else:
            error = 'invalid input data detected !'
            return render_template("error.html", error=error)
        
    return render_template("login.html")