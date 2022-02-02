from flask import Flask, redirect, render_template, request, url_for
import sys, os
sys.path.append(os.path.abspath("../"))
from auth import *
# from hashlib import blake2b
from hmac import digest


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    error = None
    errorcode = None
    login = ''
    if request.method == 'POST':
        login = request.form['login']
        passwd = request.form['passwd']
        totp = request.form['totp']
        _, errorcode, error = connection(login, passwd, totp)
        if errorcode == 0: 
            # h = blake2b(login.encode("utf-8"), digest_size=20, key=logins[login][1].encode("utf-8")).hexdigest()
            h = digest(logins[login][1].encode("utf-8"), login.encode("utf-8"), 'sha512').hex()[:32]
            # print('-'*50)
            # print(f"In index : {h}")
            # print('-'*50)
            return redirect(f"/user/{login}:{h}")
        elif errorcode == 5: 
            login = ''
        
    return render_template("index.html", error=error, errorcode=errorcode, login=login)

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    error = None
    errorcode = None
    login = ''
    if request.method == 'POST':
        login = request.form['nlogin']
        passwd = request.form['npasswd']
        confirm_passwd = request.form['cpasswd']
        _, errorcode, error = first_connection(login, passwd, confirm_passwd)
        if errorcode == 0: 
            # h = blake2b(login.encode("utf-8"), digest_size=20, key=logins[login][1].encode("utf-8")).hexdigest()
            h = digest(logins[login][1].encode("utf-8"), login.encode("utf-8"), 'sha512').hex()[:32]
            return redirect(f"/user/{login}:{h}")
        elif errorcode == 1: 
            login=''
    
    return render_template('new_user.html', error=error, errorcode=errorcode, login=login)

@app.route('/user/<user_uhash>', methods=['GET'])
def hello(user_uhash):
    # print('-'*50)
    # print(f"In hello : {user_uhash.count(':')}")
    if user_uhash.count(":") == 1:
        [user, uhash] = user_uhash.split(':')
        # print(f"user  : {user}")
        # print(f"uhash : {uhash}")
        # h = blake2b(user.encode("utf-8"), digest_size=20, key=logins[user][1].encode("utf-8")).hexdigest()
        h = digest(logins[user][1].encode("utf-8"), user.encode("utf-8"), 'sha512').hex()[:32]
        # print(f"{h}")
        # print(f"{uhash == h}")
        # print('-'*50)
        if uhash == h: 
            key = logins[user][1]
            return render_template("hello.html", user=user, key=key, image=f"{user}:{h}")
     
    return redirect("/jail")

@app.route('/qrcode/<filename_uhash>')
def display_image(filename_uhash):
    if filename_uhash.count(":") == 1:
        [user, uhash] = filename_uhash.split(':')
        # h = blake2b(user.encode("utf-8"), digest_size=20, key=logins[user][1].encode("utf-8")).hexdigest()
        h = digest(logins[user][1].encode("utf-8"), user.encode("utf-8"), 'sha512').hex()[:32]
        # print('-'*50)
        # print(f"In display : {h}")
        # print('-'*50)
        if uhash == h:
            return redirect(url_for('static', filename='qrcode/' + filename_uhash + '.png'))
    return redirect("/jail")
    


@app.route("/jail")
def jail():
    return render_template("jail.html")
    



if __name__ == "__main__":
    start_up()
    app.run() # ssl_context='adhoc', 
    shutdown()