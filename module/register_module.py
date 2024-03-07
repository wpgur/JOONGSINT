from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
import pymysql
import os
 
mysql_host = os.environ.get('MYSQL_HOST', '127.0.0.1')
mysql_port= int(os.environ.get('MYSQL_PORT', 3308))
mysql_user =  os.environ.get('MYSQL_USER', 'root')
mysql_password = os.environ.get('MYSQL_PASSWORD', '')
mysql_db = os.environ.get('MYSQL_DB', 'joongsint')

register_module = Blueprint("register_module", __name__)

@register_module.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@register_module.route("/register", methods=['GET', 'POST'])
def register_result():
    if request.method == 'POST':
        db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

        id = request.form['id']
        pw = request.form['pw']

        cursor = db.cursor()

        cursor.execute("SELECT * FROM user WHERE id = %s", (id,))
        data = cursor.fetchone()

        if data is None:
            cursor.execute("INSERT INTO user (id, pw) VALUES (%s, %s)", (id, pw))
            cursor.execute("INSERT INTO user_detail (keyword, search_ID, search_domain, search_word, user_id) VALUES ('none','none','none','none', %s)", (id))
            db.commit()
            db.close()
            return render_template("register_success.html")
        else:
            return render_template("register_fail.html")
        
    return render_template("register.html")