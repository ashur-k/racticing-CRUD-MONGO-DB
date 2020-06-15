import os
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_pymongo import PyMongo
from passlib.hash import pbkdf2_sha256


app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "randomstring123")

app.config['MONGO_DBNAME'] = 'kitchen_guide'
app.config['MONGO_URI'] = 'mongodb+srv://root:r00tUser@cluster0-dllo5.mongodb.net/kitchen_guide?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('userinfo'))

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})
    password_entered = request.form['password']
    if login_user:
        if pbkdf2_sha256.verify(password_entered, login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('userinfo'))

    return jsonify({'error': 'Invalid login credentials'})


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hash = pbkdf2_sha256.hash(request.form['password'])
            users.insert({'name': request.form['username'], 'password': hash})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return 'That username already exists!'

    return render_template('register.html')


@app.route('/userinfo')
def userinfo():
    return render_template('user_info.html',
                           users_account_info=
                           mongo.db.users_account_info.find_one({"name":session['username']}))


@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(
        host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True
    )