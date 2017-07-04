#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,url_for,render_template,redirect
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired
import random
from utility import *

#解决乱码问题
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app=Flask(__name__)
app.config['SECRET_KEY'] = 'www.ttlsa.com'

#实例化数据库类
db = DB()

global default_config

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[InputRequired()])
    submit = SubmitField('Submit')

class  LoginForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    password = PasswordField()
    remember_me = BooleanField('remember_me', default = False)

def readConfig(config_file):
    import ConfigParser
    c = ConfigParser.ConfigParser()
    c.read(config_file)
    configs = {}
    for section in c.sections():
        configs[section] = {}
        for option in c.options(section):
            configs[section][option] = c.get(section, option)

    return configs

@app.route('/', methods=['GET', 'POST'])
def index():
    with open("static/everyday.txt", 'r') as everyday:
           picked = everyday.readlines()[random.randrange(100)]
    Myform = LoginForm()
    if Myform.validate_on_submit():
        #default_config = readConfig('static/dbconf')
        db.connMySQL('10.39.54.215','flask_v1','root','123321')
        sql = "select * from login_user where name = '" + Myform.name.data + "' and password = '" + Myform.password.data + "'"
        if db.getResult(sql):
            return redirect('/main')
        else:
            return render_template("hello.html", daymessage="用户验证失败！",form=Myform)

    return render_template("hello.html", daymessage=picked, form=Myform)



@app.route('/main')
def mainpage():
    myfrom = NameForm()
    return render_template('main.html',form=myfrom)


#传一个可迭代的元素posts到前端
@app.route('/xxx')
def xxx():
    user = { 'nickname': 'Miguel' } # fake user
    posts = [ # fake array of posts
        {
            'author': { 'nickname': 'John' },
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': { 'nickname': 'Susan' },
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
        title = 'Home',
        user = user,
        posts = posts)



@app.route('/hello/', methods=['GET', 'POST'])
@app.route('/hello/<name>')
def hello(name=None):
    Myform = NameForm()
    if Myform.validate_on_submit():
        print Myform.name.data
    return render_template('hello.html', name=name, form=Myform)




@app.route('/error')
def error():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username=='admin' and password=='password':
        return render_template('hello.html', username=username)
    return render_template('form.html', message='Bad username or password', username=username)
    #return  render_template('tes.html',message=)

if __name__ == '__main__':
    app.run(host="10.39.54.215",port=5555,debug=True)
