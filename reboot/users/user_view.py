import json
from reboot.users import userdb as user
from reboot.common.session_auth import login_required
from flask import request, render_template, redirect, flash, Blueprint

users_blue = Blueprint('user_view', __name__)

@users_blue.route('/user/list/')
@login_required
def UserList():
    all_user = user.get_user()
    return render_template('user/users.html', user_list=all_user)


@users_blue.route('/user/add/', methods=['POST', 'GET'])
@login_required
def UserAdd():
    if request.method == 'GET':
        return render_template('user/user_add.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age', '')
        passwd = request.form.get('passwd', '')
        job = request.form.get('job', '')
        role_name = request.form.get('role_name', '')
        role_id = user.get_role_by_role_name(role_name)
        _is_ok, error = user.vilidate_find(name, passwd, age, job, role_name)

        if _is_ok:
            user.add_user(name, passwd, age, job, role_id)
            return json.dumps({'is_ok': _is_ok, 'error': error})
        else:
            return json.dumps({'is_ok': _is_ok, 'error': error})


@users_blue.route('/user/delete/', methods=['GET'])
@login_required
def user_delete():
    username = request.args.get('uid', '')
    if user.user_delete(username):
        flash(u'删除: %s成功' % username)
        return redirect('/user/list/')
    else:
        return '用户删除失败.'

@users_blue.route('/user/update/', methods=['POST', 'GET'])
@login_required
def user_update():
    perams = request.form
    uid = perams.get('uid', '')
    age = perams.get('age', '')
    job = perams.get('job', '')
    role_name = perams.get('role_name', '')
    role = user.get_role_by_role_name(role_name)[0][0]
    _user = user.get_user_by_id(uid=uid)[0]
    if user.user_update(uid, age, job, role):
        return json.dumps({"is_ok": True, "msg": u"更新%s成功" % _user['username']})
    else:
        return json.dumps({"is_ok": False, "msg": u"更新%s失败" % _user['username']})

@users_blue.route('/user/change-passwd/', methods=['POST'])
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

