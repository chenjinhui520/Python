import json
from reboot.assets import assets
from reboot.users import users as user

from flask import request, render_template, redirect, session, Blueprint
from reboot.common.models import Performs, Ssh
from reboot.common.session_auth import login_required

assets_blue = Blueprint('asset', __name__)

@assets_blue.route('/asset/list/', methods=['GET', 'POST'])
@login_required
def asset_list():
    assets_list = assets.get_list()
    idcs = dict(assets.get_idc())
    for asset in assets_list:
        asset['idc_name'] = idcs[asset['idc_id']]
    return render_template('/asset/asset_list.html', asset_list=assets_list)


# 创建资产信息
@assets_blue.route('/asset/create/', methods=['POST', 'GET'])
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


@assets_blue.route('/asset/update/', methods=['POST', 'GET'])
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

@assets_blue.route('/asset/delete/', methods=['GET'])
@login_required
def asset_delete():
    aid = request.args.get('aid', '')
    if assets.delete_asset(aid):
        return redirect('/asset/list')
    else:
        return '资产删除失败'


@assets_blue.route('/asset/perform/', methods=['GET', 'POST'])
@login_required
def asset_perform():
    asset_ip = request.args.get('ip')
    # cpu_list = [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
    # ram_list = [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
    # time_list = ['09:00:00', '09:10:40', '09:20:20', '09:30:10', '09:40:11', '09:50:20', '10:00:10', '10:10:10']
    time_list, cpu_list, ram_list = Performs.get_list(ip=asset_ip)
    return render_template('/asset/asset_perform.html', time_list=time_list, cpu_list=cpu_list, ram_list=ram_list)

@assets_blue.route('/asset/command/', methods=['GET', 'POST'])
@login_required
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

