from reboot import gconf
import json

def get_user():
    try:
        with open(gconf.USER_FILE, 'r') as f:
            return json.loads(f.read())
    except Exception as e:
        print(e)
        return []

def insert_user(**kwargs):
    for v in kwargs.values():
        if v == '':
            return 'name,pass,job,age can not be null'
    users = get_user()
    for user in users:
        if kwargs['name'] == user['name']:
            return 'add failed, user exist!'
    users.append(kwargs)
    if save_users(users):
        return 'add user success!'
    else:
        return 'add user failed!'

def update_user(**kwargs):
    users = get_user()
    for user in users:
        if user['name'] == kwargs['name']:
            user.update(kwargs)
            break
    if save_users(users):
        return 'update user success!'
    else:
        return 'update user failed!'

def del_user(username):
    users = get_user()
    for index, user in enumerate(users):
        if username == user['name']:
            del users[index]
            if save_users(users):
                return 'del user success!'
            else:
                return 'del user failed!'


def save_users(users):
    try:
        with open(gconf.USER_FILE, 'w') as f:
            f.write(json.dumps(users))
        return True
    except (FileNotFoundError, FileExistsError):
        return False


def validate_login(username, password):
    for user in get_user():
        if username == user.get('name') and password == user.get('passwd'):
            return True
        return False


if __name__ == '__main__':
    print(get_user())


