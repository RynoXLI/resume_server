from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import yaml
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config import message_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# load the config file
conf = yaml.load(open("config/site_config.yml", "r"), Loader=yaml.Loader)

# start smtp connection
s = smtplib.SMTP(host=conf['smtp']['hostname'], port=conf['smtp']['port'])
# s.starttls()
# s.login(user="", password="")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    pub_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Post %r' % self.email


@app.route('/', methods=["GET", "POST"])
def new_home():
    now = datetime.now()

    if request.method == "POST":
        email = request.form.get("email")
        fname = request.form.get('firstname')
        lname = request.form.get('lastname')
        msg = request.form.get('msg')
        send_email = request.form.get('sendemail')
        print(f"Email:{email}, fname:{fname}, lname:{lname}, msg:{msg}, send_email:{send_email}")

        if email and fname and lname and msg:
            p = Post(email=email, fname=fname, lname=lname, msg=msg)
            db.session.add(p)
            db.session.commit()

        if send_email and email and fname and lname and msg:
            email_msg = MIMEMultipart()
            message = message_template.substitute(fname=fname,
                                                  lname=lname,
                                                  email=email,
                                                  msg=msg,
                                                  time=now)

            # setup msg parms
            email_msg['From'] = "localhost"
            email_msg['To'] = email
            email_msg['Subject'] = "Message Record"
            email_msg.attach(MIMEText(message, 'plain'))

            s.send_message(email_msg)
            print("Sending email...")

    return render_template('base.html', time=now, conf=conf['index'])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
