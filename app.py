from flask import Flask, render_template
import yaml
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def home():
    now = datetime.now()
    return render_template('index.html', time=now)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
