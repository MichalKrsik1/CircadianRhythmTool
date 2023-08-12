from flask import Flask, render_template
from tool1 import tool1_home, tool1_submit
from tool2 import tool2_home, tool2_submit
import secrets
from flask_session import Session


class ConfigureFlaskApp:
    def __init__(self, flask_app):
        flask_app.secret_key = secrets.token_hex(32)
        flask_app.config['SESSION_TYPE'] = 'filesystem'
        Session(flask_app)


app = Flask(__name__)
ConfigureFlaskApp(app)  # This will configure your Flask app


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


app.add_url_rule('/tool1', 'tool1_home', tool1_home)
app.add_url_rule('/tool1/submit', 'tool1_submit', tool1_submit, methods=['POST'])

app.add_url_rule('/tool2', 'tool2_home', tool2_home)
app.add_url_rule('/tool2/submit', 'tool2_submit', tool2_submit, methods=['POST'])


if __name__ == '__main__':
    app.run(debug=True)
