import json
from reboot import gconf, assets, userdb as user

from flask import Flask, request, render_template, redirect, session, flash
from functools import wraps
from reboot.models import Performs, Ssh
from reboot.dbutils import MySQLconnection
from functools import reduce

app = Flask(__name__)
app.secret_key = '13123dfasdf'

# 登陆验证装饰器
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not session:
            return redirect('/login/')
        ret = func(*args, **kwargs)
        return ret
    return inner


@app.route('/')
@login_required
def log_status():
    sql = 'select distinct status from accesslog'
    count, status_list = MySQLconnection.execute_sql1(sql)
    status_list = [i[0] for i in status_list]
    status_dict = {i: MySQLconnection.execute_sql1('select count(*) from accesslog where status=%s',
                                                   (i,))[1][0][0] for i in status_list}
    total = reduce(lambda x, y: x+y, status_dict.values())
    data = [['%s' % k, round(v/total, 3)*100] for k, v in status_dict.items()]
    return render_template('/public/index_body.html', data=data)

@app.route('/logs/')
@login_required
def logs():
    topn = request.args.get('topn')
    # 三目表达式
    topn = int(topn) if str(topn).isdigit() else 10
    title = 'Reboot'
    log_list = user.get_accesslog(topn)
    return render_template('user/logs.html', title=title, logall_list=log_list)


@app.route('/login/', methods=['POST', 'GET'])
def Login():
    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        if user.vilidate_login(username, password):
            session['user'] = {'username': username}
            # 跳转到首页
            return redirect('/user/list/')
        else:
            return render_template('login.html', username=username, error=u'用户名或密码错误!')

@app.route('/user/list/')
@login_required
def UserList():
    all_user = user.get_user()
    return render_template('user/user_list.html', user_list=all_user)

@app.route('/user/add/', methods=['POST', 'GET'])
@login_required
def UserAdd():
    name = request.form.get('name')
    age = request.form.get('age', '')
    passwd = request.form.get('passwd', '')
    job = request.form.get('job', '')
    if request.method == 'GET':
        return render_template('user/user_add.html')
    elif request.method == 'POST':
        _is_ok, error = user.vilidate_find(name, passwd, age, job)
        if _is_ok:
            count = user.add_user(name, passwd, age, job)
            print(count)
            return json.dumps({'is_ok': _is_ok, 'error': error})
        else:
            return json.dumps({'is_ok': _is_ok, 'error': error})


@app.route('/user/delete/', methods=['GET'])
@login_required
def user_delete():
    username = request.args.get('uid', '')
    if user.user_delete(username):
        flash(u'删除: %s成功' % username)
        return redirect('/user/list/')
    else:
        return '用户删除失败.'

@app.route('/user/update/', methods=['POST', 'GET'])
@login_required
def user_update():
    perams = request.args if request.method == 'GET'else request.form
    uid = perams.get('uid', '')
    age = perams.get('age', '')
    job = perams.get('job', '')
    _user = user.get_user_by_id(uid=uid)[0]
    if request.method == 'GET':
        return render_template('user/user_update.html', _user=_user)
    if user.user_update(uid, age, job):
        return json.dumps({"is_ok": True, "msg": u"更新%s成功" % _user['username']})
    else:
        return json.dumps({"is_ok": False, "msg": u"更新%s失败" % _user['username']})

@app.route('/user/change-passwd/', methods=['POST'])
@login_required
def change_passwd():
    userid = request.form.get('userid')
    username = request.form.get('username')
    original_passwd = request.form.get('original-passwd')
    new_passwd = request.form.get('new-passwd')
    new_repasswd = request.form.get('new-repasswd')
    is_ok, error = user.vilidate_change_user_passwd(userid, username, original_passwd, new_passwd, new_repasswd)
    if is_ok:
        user.change_user_passwd(userid, new_passwd)
    return json.dumps({"is_ok": is_ok, "error": error})


# 用户登出
@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/login/')


@app.route('/asset/list/', methods=['GET', 'POST'])
def asset_list():
    assets_list = assets.get_list()
    idcs = dict(assets.get_idc())
    for asset in assets_list:
        asset['idc_name'] = idcs[asset['idc_id']]
    return render_template('/asset/asset_list.html', asset_list=assets_list)


# 创建资产信息
@app.route('/asset/create/', methods=['POST', 'GET'])
@login_required
def asset_create():
    perams = request.args if request.method == 'GET'else request.form
    lists = ['sn', 'ip', 'hostname', 'idc_id', 'purchase_date', 'warranty',
             'vendor', 'model', 'admin', 'business', 'cpu', 'ram', 'disk', 'os']
    asset_dict = {}
    for i in lists:
        asset_dict['_'+i] = perams.get(i)
    if request.method == 'GET':
        return render_template('asset/asset_create.html', idcs=assets.get_idc())
    else:
        # 1、验证用户数据合法性；
        _is_ok, error = assets.vilidate_create_asset(asset_dict)
        # 2、如果合法，入库；
        if _is_ok:
            # 数据入库
            assets.create_asset(asset_dict)
            return json.dumps({'is_ok': _is_ok, 'error': u'资产添加成功'})
        else:
            return json.dumps({'is_ok': _is_ok, 'error': error})


@app.route('/asset/update/', methods=['POST', 'GET'])
@login_required
def asset_update():
    perams = request.args if request.method == 'GET'else request.form
    sn = perams.get('sn')
    asset = assets.get_asset_by_sn(sn)
    idcs = assets.get_idc()
    for idc in idcs:
        if idc[0] == asset['idc_id']:
            selected = asset['idc_id']
    if request.method == 'GET':
        return render_template('asset/asset_update.html', asset=asset, idcs=idcs, selected=selected)
    else:
        lists = ['ip', 'hostname', 'idc_id', 'purchase_date', 'warranty',
                 'vendor', 'model', 'admin', 'business', 'cpu', 'ram', 'disk', 'os']
        asset_dict = {}
        for i in lists:
            asset_dict['_'+i] = perams.get(i)
        _is_ok, error = assets.vilidate_update_asset(asset_dict)
        if _is_ok:
            assets.update_asset(sn, asset_dict)
            return json.dumps({'is_ok': _is_ok, 'error': u'资产更新成功'})
        else:
            return json.dumps({'is_ok': _is_ok, 'error': error})

@app.route('/asset/delete/', methods=['GET'])
@login_required
def asset_delete():
    aid = request.args.get('aid', '')
    if assets.delete_asset(aid):
        return redirect('/asset/list')
    else:
        return '资产删除失败'


@app.route('/performs/', methods=['GET', 'POST'])
def performs():
    # msg = {u'ip': u'192.168.0.3', u'ram': 31.810766721044047,
    # u'cpu': 2.9000000000000057, u'time': u'2018-02-10 18:30:11'}
    # app_key = request.args.get('app_key')
    # app_secret = request.args.get('app_secret')

    app_key = request.headers.get('app_key', '')
    app_secret = request.headers.get('app_secret', '')
    if app_key != gconf.app_key or app_secret != gconf.app_secret:
        return json.dumps({'code': 400, 'text': '认证失败'})

    msg = request.get_json()
    Performs.add(msg)
    return json.dumps({'is_ok': True})


@app.route('/asset/perform/', methods=['GET', 'POST'])
def asset_perform():
    asset_ip = request.args.get('ip')
    # cpu_list = [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
    # ram_list = [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
    # time_list = ['09:00:00', '09:10:40', '09:20:20', '09:30:10', '09:40:11', '09:50:20', '10:00:10', '10:10:10']
    time_list, cpu_list, ram_list = Performs.get_list(ip=asset_ip)
    return render_template('/asset/asset_perform.html', time_list=time_list, cpu_list=cpu_list, ram_list=ram_list)

@app.route('/asset/command/', methods=['GET', 'POST'])
def asset_command():
    perams = request.args if request.method == 'GET' else request.form
    asset_ip = perams.get('ip')
    _mpasswd = perams.get('mpassword')
    if request.method == 'GET':
        info = u'这里是返回的结果信息'
        return render_template('/asset/asset_command.html', ip=asset_ip, info=info)
    else:
        _status = user.vilidate_login(session['user']['username'], _mpasswd)
        info = []
        if _status:
            cmd_list = perams.get('command', '').split(';')
            ssh = Ssh(host='127.0.0.1', cmds=cmd_list)
            _rt_list = ssh.ssh_execute()
            for cmd, out, err in _rt_list:
                info.append([out, err])
        return json.dumps({'status': _status, 'info': info})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

