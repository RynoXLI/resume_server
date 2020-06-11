from flask import Flask, render_template
import yaml
from datetime import datetime

app = Flask(__name__)

conf = yaml.load(open("config/site_config.yml", "r"), Loader=yaml.Loader)


@app.route('/')
def home():
    now = datetime.now()
    return render_template('index.html', time=now)


@app.route('/new')
def new_home():
    now = datetime.now()
    return render_template('base.html', time=now, conf=conf['index'])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
