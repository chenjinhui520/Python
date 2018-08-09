from flask import redirect, session
from functools import wraps


# 登陆验证装饰器
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not session.get('user', None):
            return redirect('/login/')
        ret = func(*args, **kwargs)
        return ret
    return inner

