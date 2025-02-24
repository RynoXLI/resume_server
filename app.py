import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import boto3
import os
import imghdr

import jinja2
import yaml
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, abort
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
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["UPLOAD_FOLDER"] = 'uploads'
app.config["UPLOAD_EXTENSIONS"] = ['.jpg', '.png', '.gif']
app.add_url_rule('/uploads/<path:filename>', endpoint='uploads', view_func=app.send_static_file)

db = SQLAlchemy(app)

# load the config file
conf = yaml.load(open("config/site_config.yml", "r"), Loader=yaml.Loader)

# load email_info.yml
email_info = yaml.load(open("config/email_info.yml", "r"), Loader=yaml.Loader)

# load aws_config.yml
aws_config = yaml.load(open("config/aws_config.yml", "r"), Loader=yaml.Loader)

# load ec2
session = boto3.Session(
    aws_access_key_id=aws_config["access_key_id"],
    aws_secret_access_key=aws_config["secret_access_key"],
    region_name=aws_config['region']
)

ec2 = session.client("ec2")

message_template = (
    "Someone sent a message!\n"
    "First Name: ${fname};\n"
    "Last Name: ${lname};\n"
    "Email Address: ${email};\n"
    "Message: ${msg};\n"
    "Time Stamp: ${time};"
)
message_template = Template(message_template)

def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    """
    Download the contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

# os.system(f'aws s3 sync uploads s3://{aws_config["bucket"]}/uploads')
# sync.S3Sync(session).sync('uploads', f"{aws_config['bucket']}")

download_s3_folder(aws_config['bucket'], 'uploads')

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
    return render_template("index.html", base=conf["base"], conf=conf["index"])


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
    return render_template("morgan.html", base=conf["base"], files=list_files())


@app.route("/factorio")
def factorio():
    return render_template("gameserver.html", base=conf["base"], name='factorio')


@app.route('/valheim')
def valheim():
    return render_template('gameserver.html', base=conf['base'], name='valheim')


@app.route('/start/<name>')
def start_instance(name):
    if name not in ["factorio", "valheim"]:
        return 404
    try:
        ec2.start_instances(InstanceIds=[aws_config[f"{name}_instance"]])
    except:
        return jsonify({"status": "Error starting. Try again in two minutes"})

    return jsonify({"status": "Server Starting"})


@app.route("/stop/<name>")
def stop_instance(name):
    if name not in ['factorio', 'valheim']:
        return 404
    try:
        ec2.stop_instances(InstanceIds=[aws_config[f"{name}_instance"]])
    except:
        return jsonify({"status": "Error stopping"})

    return jsonify({"status": "Server Stopping"})

@app.route('/status/<name>')
def get_status(name):
    if name not in ['factorio', 'valheim']:
        return 404
    try:
        instance =session.resource("ec2").Instance(aws_config[f"{name}_instance"])
        state = instance.state["Name"]
    except:
        state = "N/A"
    return jsonify({"status": state})

@app.route('/ipaddress/<name>')
def ip_address(name):
    if name not in ['factorio', 'valheim']:
        return jsonify({'IP': "N/A"})
    ip = get_ip(name)
    return jsonify({"IP": ip})


@app.errorhandler(404)
def error_404(e):
    now = datetime.now()
    return render_template("error_404.html", time=now, base=conf["base"]), 404


def get_ip(name):
    try:
        instance = ec2.describe_instances(InstanceIds=[aws_config[f"{name}_instance"]])
        ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        return ip
    except:
        return "N/A"

def upload_file(file_name, bucket=aws_config['bucket']):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = session.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response

def download_file(file_name, bucket=aws_config['bucket']):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = session.resource('s3')
    output = f"downloads/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)

    return output

def list_files(bucket=aws_config['bucket'], prefix='uploads/'):
    """
    Function to list files in a given S3 bucket
    """
    s3 = session.resource('s3')
    contents = []
    photo_bucket = s3.Bucket(aws_config['bucket'])

    for s3_obj in photo_bucket.objects.filter(Prefix=prefix):
        file_name = s3_obj.key.replace(prefix, '', 1)
        
        if file_name != "":
            contents.append(file_name)

    return contents

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        filename = secure_filename(f.filename)
        if f.filename != '':
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(f.stream):
                abort(400)
            else: 
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            upload_file(f"uploads/{filename}")

        return redirect(url_for('morgan'))
    return render_template('upload.html', base=conf['base'])


@app.route('/uploads/<filename>')
def get_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/testlist')
def test_list():
    return jsonify({'msg': list_files(prefix='uploads/')})


if __name__ == "__main__":
    app.run(port=5000, host="localhost", debug=True)
