from asilib import ASIConnection

conf = {
    'base_url': 'http://cos.alpha.sizl.org',
    'app_name': 'myapp',
    'app_password': 'secret',
    'username': 'joeuser',
    'password': 'hidden',
}

uid = '12345678'
with ASIConnection(**conf) as uc:
    user = uc.get_user(uid)
    friends = uc.get_friends(uid)
    print('User %s has %i friends' % (user.username, len(friends)))
