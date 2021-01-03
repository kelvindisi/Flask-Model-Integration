from flask import Flask, render_template, request, Blueprint, flash, g, redirect, session, url_for, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pickle
import Database_Conn as db
import jwt
import Database_Configs  as  config
import hashlib

app = Flask(__name__)
# Model
model = pickle.load(open('GreenGrams.pkl', 'rb'))
cursor, conn = db.connection(app)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('home'))
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        cursor.execute('SELECT * FROM auth WHERE email=%s', (email))
        user = cursor.fetchone()
        app.logger.debug(user)
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[4], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        flash(error)
        return render_template('login.html', title='Login')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('home'))
        return render_template('register.html', title='Register')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm']
        error = None
        if password != confirm:
            error = 'password and confirm password does not match'
        else:
            cursor.execute('SELECT * FROM auth WHERE email=%s', (email))
            user = cursor.fetchone()
            app.logger.debug(user)
            if user:
                error = 'Sorry, email already exist!'

        if error is None:
            password = generate_password_hash(password)
            cursor.execute('INSERT into auth (name, phone, email, password) VALUES (%s,%s,%s,%s)', (name, phone, email, password))
            user = cursor.fetchone()
            conn.commit()
            if cursor.lastrowid:
                flash('Registration successfull!, login now!')
                return redirect(url_for('login'))
            else:
                flash('Something went wrong, try again!')
                return render_template('register.html', title='Register')
        flash(error)
        return render_template('register.html', title='Register')

@app.route('/')
def index():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE user_id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[3]
    return render_template('home.html', title=name, name=name)


@app.route('/profile')
def profile():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE user_id=%s', (session['user_id']))
    user = cursor.fetchone()
    emails = user[3]
    phones = user[2]
    names = user[1]
    return render_template('profile.html', title=names, email=emails, phone=phones, name=names)



@app.route('/profileupdate', methods=('GET', 'POST'))
def profileupdate():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('profile'))
        return render_template('register.html', title='Register')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone'] 
        error = None
        if email != "":
            cursor.execute('SELECT * FROM auth WHERE email=%s', (email))
            user = cursor.fetchone()
            app.logger.debug(user)
            # if user:
            #     error = 'Sorry, email already exist!'

        if error is None: 
            Updd = ("UPDATE auth SET name = %s,phone = %s WHERE email = %s")  
            vall = (name, phone,email)
            cursor.execute(Updd,vall)
            user = cursor.fetchone()
            conn.commit()
            if cursor:
                flash('Updated successfull!')
                return redirect(url_for('profile'))
            else:
                flash('Something went wrong, try again!')
                return render_template('profile.html', title='User Account')
        flash(error)
        return render_template('profile.html', title='User Account')




@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out.')
    return redirect('/login')



@app.route('/history')
def history(): 
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE user_id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[3]
    return render_template('history.html', title=name, name=name)
 



@app.route('/predpred')
def predpred():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE user_id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[3]
    return render_template('as.html', title=name, name=name)





@app.route('/predict',methods=['POST'])
def predict():

    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)

    return render_template('as.html', prediction_text='Sales should be $ {}'.format(output))



@app.route('/results',methods=['POST'])
def results():

    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]

if __name__ == '__main__':
    app.debug = config.debug
    app.config['SECRET_KEY'] = config.secret
    app.run(port=config.port)
