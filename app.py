import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import boto3

import jinja2
import yaml
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import (
    Form,
    BooleanField,
    StringField,
    validators,
    TextAreaField,
    SubmitField,
)
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

# load the config file
conf = yaml.load(open("config/site_config.yml", "r"), Loader=yaml.Loader)

# load email_info.yml
email_info = yaml.load(open("config/email_info.yml", "r"), Loader=yaml.Loader)

# load aws_config.yml
aws_config = yaml.load(open("config/aws_config.yml", "r"), Loader=yaml.Loader)

# load ec2
ec2 = boto3.client('ec2')

message_template = (
    "Someone sent a message!\n"
    "First Name: ${fname};\n"
    "Last Name: ${lname};\n"
    "Email Address: ${email};\n"
    "Message: ${msg};\n"
    "Time Stamp: ${time};"
)
message_template = Template(message_template)


class Message(Form):
    email = EmailField("Email Address", [validators.DataRequired(), validators.Email()])
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
        return "<Post %r" % self.email


@app.route("/")
def home():
    now = datetime.now()
    return render_template(
        "index.html", base=conf["base"], conf=conf["index"]
    )


@app.route("/message", methods=["GET", "POST"])
def message():
    now = datetime.now()
    form = Message(request.form)
    form.lname()
    if request.method == "POST" and form.validate():
        print(
            f"Email:{form.email.data}, fname:{form.fname.data}, lname:{form.lname.data}, msg:{form.msg.data}, cc:{form.cc.data}"
        )

        p = Post(
            email=form.email.data,
            fname=form.fname.data,
            lname=form.lname.data,
            msg=form.msg.data,
            pub_time=now,
        )
        db.session.add(p)
        db.session.commit()

        recieve_email = form.email.data

        formated_time = now.strftime("%Y-%m-%d %I:%M %p")

        if form.cc.data:
            # setup email
            templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
            templateEnv = jinja2.Environment(loader=templateLoader)
            TEMPLATE_FILE = "email.html"
            template = templateEnv.get_template(TEMPLATE_FILE)
            outputText = template.render(
                fname=form.fname.data.title(), msg=form.msg.data, pub_time=formated_time
            )  # this is where to put args to the template renderer

            email_msg = MIMEMultipart()
            email_msg.attach(MIMEText(outputText, "html"))

            # setup msg parms
            email_msg["From"] = email_info["email"]
            email_msg["Subject"] = "Message Record"
            email_msg["To"] = recieve_email
            send_email(recieve_email, email_msg)

        plain_msg = message_template.substitute(
            fname=form.fname.data,
            lname=form.lname.data,
            email=form.email.data,
            msg=form.msg.data,
            time=formated_time,
        )
        # send to myself
        email_msg_copy = MIMEMultipart()
        email_msg_copy.attach(MIMEText(plain_msg, "plain"))

        # setup msg parms
        email_msg_copy["From"] = email_info["email"]
        email_msg_copy["Subject"] = "Message Record"
        email_msg_copy["To"] = email_info["cc_to"]
        send_email(email_info["cc_to"], email_msg_copy)

        return redirect(url_for("thankyou"))

    return render_template("message.html", time=now, base=conf["base"], form=form)


def send_email(recipients, email_msg):
    context = ssl.create_default_context()
    with smtplib.SMTP(email_info["smtp"], email_info["port"]) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(email_info["email"], email_info["password"])
        server.sendmail(email_info["email"], recipients, email_msg.as_string())


@app.route("/thankyou")
def thankyou():
    now = datetime.now()
    return render_template("thankyou.html", time=now, base=conf["base"])


@app.route("/more")
def more():
    now = datetime.now()
    return render_template("more.html", time=now, base=conf["base"], conf=conf["more"])


@app.route("/morgan")
def morgan():
    return render_template("morgan.html", base=conf['base'])


@app.route("/factorio")
def factorio():
    return render_template("factorio.html", base=conf['base'])

@app.route("/abe424")
def abe424():
    return render_template("abe424.html", base=conf['base'])


@app.route('/startfactorio')
def start_factorio():
    try:
        ec2.start_instances(InstanceIds=[aws_config['factorio_instance']])
    except:
        return jsonify({'status': 'Error starting. Try again in two minutes'})

    return jsonify({"status": "Server Starting"})


@app.route('/startabe424')
def start_abe424():
    try:
        ec2.start_instances(InstanceIds=[aws_config['abe424_instance']])
    except:
        return jsonify({'status': 'Error starting. Try again in two minutes'})

    return jsonify({"status": "Server Starting"})


@app.route('/stopfactorio')
def stop_factorio():
    try:
        ec2.stop_instances(InstanceIds=[aws_config['factorio_instance']])
    except:
        return jsonify({"status": "Error stopping"})

    return jsonify({"status": "Server Stopping"})


@app.route('/stopabe424')
def stop_abe424():
    try:
        ec2.stop_instances(InstanceIds=[aws_config['abe424_instance']])
    except:
        return jsonify({"status": "Error stopping"})

    return jsonify({"status": "Server Stopping"})


@app.route('/factoriostatus')
def factorio_status():
    try:
        instance = boto3.resource('ec2').Instance(aws_config['factorio_instance'])
        state = instance.state['Name']
    except:
        state = "N/A"
    return jsonify({"status": state})


@app.route('/abe424status')
def abe424_status():
    try:
        instance = boto3.resource('ec2').Instance(aws_config['abe424_instance'])
        state = instance.state['Name']
    except:
        state = "N/A"
    return jsonify({"status": state})


@app.route('/ipaddress')
def ip_address():
    ip = get_ip()
    return jsonify({"IP": ip})


@app.route('/ipabe424address')
def ip_abe424_address():
    ip = get_abe424_ip()
    return jsonify({"IP": ip})


@app.errorhandler(404)
def error_404(e):
    now = datetime.now()
    return render_template("error_404.html", time=now, base=conf["base"]), 404


def get_ip():
    try:
        instance = ec2.describe_instances(InstanceIds=[aws_config['factorio_instance']])
        ip = instance['Reservations'][0]["Instances"][0]["PublicIpAddress"]
        return ip
    except:
        return "N/A"


def get_abe424_ip():
    try:
        instance = ec2.describe_instances(InstanceIds=[aws_config['abe424_instance']])
        ip = instance['Reservations'][0]["Instances"][0]["PublicIpAddress"]
        return ip
    except:
        return "N/A"


if __name__ == "__main__":
    app.run(port=5000, host='localhost', debug=True)
