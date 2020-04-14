from flask import Flask

from src.flask.mock_blueprint import mock_blueprint
from src.flask.templates_blueprint import template_blueprint
from src.flask.user_blueprint import user_blueprint

app = Flask(__name__)
app.register_blueprint(user_blueprint)
app.register_blueprint(template_blueprint)
app.register_blueprint(mock_blueprint)
