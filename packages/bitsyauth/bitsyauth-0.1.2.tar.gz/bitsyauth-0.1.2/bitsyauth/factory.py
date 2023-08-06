from bitsyauth import BitsyAuth
from paste.auth import digest

def passworder_factory(username, database):
    def passwords():
        passwords = database.passwords()
        password = passwords[username]
        return {username: password}
    return passwords

def filter_factory(global_conf, **app_conf):

    user = app_conf['user']
    site = app_conf.get('site', 'bitsyauth')
    secret = app_conf.get('secret', 'secret')

    from bitsyblog.user import FilespaceUsers

    users_directory = FilespaceUsers(
        app_conf['users_directory'])

    passwords = passworder_factory(user, users_directory)

    def filter(app):
        ret = BitsyAuth(
            app,
            global_conf,
            passwords,
            newuser=None,
            site=site,
            secret=secret)
        return ret
    return filter
