from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
import pymysql
 
mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'root'
mysql_password = '7575'
mysql_db = 'devops'

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

        cursor.execute("SELECT * FROM login_table WHERE id = %s", (id,))
        data = cursor.fetchone()

        if data is None:
            cursor.execute("INSERT INTO login_table (id, pw) VALUES (%s, %s)", (id, pw))
            db.commit()
            db.close()
            return render_template("register_success.html")
        else:
            return render_template("register_fail.html")
        
    return render_template("register.html")