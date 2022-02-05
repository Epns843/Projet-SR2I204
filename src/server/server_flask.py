from flask import Flask, redirect, render_template, request, url_for, make_response, send_from_directory
import sys, os, time
import qrcode
from rm import rm 
sys.path.append(os.path.abspath("../"))
from auth import *

session_ids = dict()

login_tries = dict()
timeout = dict()
timeout_time = 300

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
        if login not in timeout.keys() or time.time() > timeout[login]:
            _, errorcode, error = connection(login, passwd, totp)
            if login in timeout.keys(): 
                timeout.pop(login)
        else: 
            return redirect("/")
        if errorcode == 0: 
            try: 
                timeout.pop(login)
                login_tries.pop(login)
            except:
                pass
            session_id = get_session_id(login)
            session_ids[login] = session_id
            
            img = get_qrcode(login)
            img.save(f"static/qrcode/{login}.png")

            res = make_response(redirect(f"/user/{login}"))
            res.set_cookie('session_id', session_id)
            return res
        elif errorcode == 5: 
            login = ''
        else:
            if login not in login_tries.keys():
                login_tries[login] = 3
            
            login_tries[login] -= 1
            if login_tries[login] != 0: 
                if login_tries[login] == 1:
                    error += f" ({login_tries[login]} attempt left)"
                elif login_tries[login] == 2: 
                    error += f" ({login_tries[login]} attempts left)"
                    
            else: 
                timeout[login] = time.time()+timeout_time
                return redirect("/")
                
            
        
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
            session_id = get_session_id(login)
            session_ids[login] = session_id
            
            img = get_qrcode(login)
            img.save(f"static/qrcode/{login}.png")
            
            res = make_response(redirect(f"/user/{login}"))
            res.set_cookie('session_id', session_id)
            return res
        elif errorcode == 1: 
            login=''
    
    return render_template('new_user.html', error=error, errorcode=errorcode, login=login)

@app.route('/user/<user>', methods=['GET', 'POST'])
def hello(user):    
    if(user in session_ids.keys() and session_ids[user] == request.cookies.get('session_id')):
        if request.method == 'GET': 
            key = decrypt_key(logins[user][1])
            return render_template("hello.html", user=user, key=key, filename=f"{user}.png")
        else: 
            rm(f"static/qrcode/{user}.png")
            res = make_response(redirect(f"/"))
            res.set_cookie('session_id', session_ids[user], max_age=0)
            session_ids.pop(user)
            return res
    if request.method == 'POST': 
        res = make_response(redirect(f"/"))
        res.set_cookie('session_id', "", max_age=0)
        return res
    return redirect("/jail")


@app.route('/static/qrcode/<image>')
def image(image):
    
    user = image[:-4]
    if(user in session_ids.keys() and session_ids[user] == request.cookies.get('session_id')):
        return send_from_directory("static/qrcode/", f"{image}")
    else: 
        return redirect("/jail")
    


@app.route("/jail")
def jail():
    return render_template("jail.html")
    



if __name__ == "__main__":
    start_up()
    # app.run(debug=True)
    app.run(ssl_context='adhoc')  
    # app.run(host='172.16.85.1')  
    shutdown()