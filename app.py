from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
import yaml
from datetime import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config import message_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# load the config file
conf = yaml.load(open("config/site_config.yml", "r"), Loader=yaml.Loader)

# load email_info.yml
email_info = yaml.load(open("config/email_info.yml", 'r'), Loader=yaml.Loader)


class Message(Form):
     email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
     fname = StringField("First Name", [validators.Length(min=1, max=60)])
     lname = StringField("Last Name", [validators.Length(min=1, max=60)])
     msg = TextAreaField("Message", [validators.DataRequired()])
     cc = BooleanField("Email Copy")
     submit = SubmitField("Submit")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    pub_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Post %r' % self.email


@app.route('/')
def home():
    now = datetime.now()
    return render_template('index.html', time=now, conf=conf['index'])


@app.route('/message', methods=['GET', 'POST'])
def message():
    now = datetime.now()
    form = Message(request.form)
    form.lname()
    if request.method == "POST" and form.validate():
        print(f"Email:{form.email.data}, fname:{form.fname.data}, lname:{form.lname.data}, msg:{form.msg.data}, cc:{form.cc.data}")

        p = Post(email=form.email.data, fname=form.fname.data, lname=form.lname.data, msg=form.msg.data, pub_time=now)
        db.session.add(p)
        db.session.commit()

        if form.cc.data:
            email_msg = MIMEMultipart()
            message = message_template.substitute(fname=form.fname.data,
                                                  lname=form.lname.data,
                                                  email=form.email.data,
                                                  msg=form.msg.data,
                                                  time=now)

            # setup msg parms
            email_msg['From'] = email_info['email']
            email_msg['To'] = form.email.data
            email_msg['Subject'] = "Message Record"
            email_msg.attach(MIMEText(message, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP(email_info['smtp'], email_info['port']) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(email_info['email'], email_info['password'])
                server.sendmail(email_info['email'], form.email.data, email_msg)

        return redirect(url_for('thankyou'))

    return render_template('message.html', time=now, conf=conf['index'], form=form)


@app.route('/thankyou')
def thankyou():
    now = datetime.now()
    return render_template('thankyou.html', time=now, conf=conf['index'])


@app.route('/more')
def more():
    now = datetime.now()
    return render_template('more.html', time=now, conf=conf['index'])


@app.errorhandler(404)
def error_404(e):
    now = datetime.now()
    return render_template('error_404.html', time=now, conf=conf['index']), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)
