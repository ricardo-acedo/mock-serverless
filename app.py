from flask import Flask

from src.flask.templates_blueprint import template_blueprint
from src.flask.user_blueprint import user_blueprint

app = Flask(__name__)
app.register_blueprint(user_blueprint)
app.register_blueprint(template_blueprint)
