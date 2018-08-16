import json
import configparser
from reboot.users import users as user

from flask import request, render_template, redirect, session, Blueprint
from reboot.common.models import Performs
from reboot.common.dbutils import MySQLHelper
from functools import reduce
from reboot.common.session_auth import login_required

db = MySQLHelper()
common_blue = Blueprint('common_view', __name__)

@common_blue.route('/')
@login_required
def log_status():
    sql = 'select distinct status from accesslog'
    count, status_list = db.fetch_all(sql)
    status_list = [i[0] for i in status_list]
    print(status_list)
    status_dict = {i: db.fetch_all('select count(*) from accesslog where status=%s',
                                   (i,))[1][0][0] for i in status_list}
    total = reduce(lambda x, y: x+y, status_dict.values())
    data = [['%s' % k, round(v/total, 3)*100] for k, v in status_dict.items()]
    return render_template('/public/index_body.html', data=data)

@common_blue.route('/logs/')
@login_required
def logs():
    topn = request.args.get('topn')
    # 三目表达式
    topn = int(topn) if str(topn).isdigit() else 10
    title = 'Reboot'
    log_list = user.get_accesslog(topn)
    return render_template('user/logs.html', title=title, logall_list=log_list)


@common_blue.route('/login/', methods=['POST', 'GET'])
def Login():
    username = request.form.get('username')
    password = request.form.get('password')
    role = user.get_role_from_username(username)
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        if user.vilidate_login(username, password):
            session['user'] = {'username': username, 'role': role[0][0]}
            # 跳转到首页
            return redirect('/user/list/')
        else:
            return render_template('login.html', username=username, error=u'用户名或密码错误!')


@common_blue.route('/performs/', methods=['GET', 'POST'])
def performs():
    # msg = {u'ip': u'192.168.0.3', u'ram': 31.810766721044047,
    # u'cpu': 2.9000000000000057, u'time': u'2018-02-10 18:30:11'}
    # app_key = request.args.get('app_key')
    # app_secret = request.args.get('app_secret')

    app_key = request.headers.get('app_key', '')
    app_secret = request.headers.get('app_secret', '')
    conf = configparser.ConfigParser()
    conf.read('conf/reboot.conf')
    if app_key != conf.get('session', 'app_key') or app_secret != conf.get('session', 'app_secret'):
        return json.dumps({'code': 400, 'text': '认证失败'})

    msg = request.get_json()
    Performs.add(msg)
    return json.dumps({'is_ok': True})


# 用户登出
@common_blue.route('/logout/')
def logout():
    session.clear()
    return redirect('/login/')


