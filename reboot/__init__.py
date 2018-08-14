import configparser

from flask import Flask

from reboot.users import user_view
from reboot.assets import assets_view
from reboot.common import common_view

app = Flask(__name__)
conf = configparser.ConfigParser()
conf.read('conf/reboot.conf')
app.config['SECRET_KEY'] = conf.get('session', 'app_secret')

app.register_blueprint(user_view.users_blue)
app.register_blueprint(assets_view.assets_blue)
app.register_blueprint(common_view.common_blue)

