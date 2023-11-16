from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
import pymysql
 
mysql_host = 'localhost'
mysql_port=3308
mysql_user = 'root'
mysql_password = ''
mysql_db = 'db_board'

register_module = Blueprint("register_module", __name__)

@register_module.route("/register", methods=['GET', 'POST'])
def register_result():
    if request.method == 'POST':
        error = None

        db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

        id = request.form['id']
        pw = request.form['pw']

        cursor = db.cursor()

        sql = "SELECT id FROM member WHERE id = %s AND password = %s"
        value = (id, pw)

        cursor.execute(sql, value)

        data = cursor.fetchone()
        db.commit()
        db.close()

        if data:
            session['login_user'] = data[0]
        else:
            error = 'invalid input data detected !'
        return render_template("login.html", user_id=data[0])
        
    
    
    return render_template("register.html")