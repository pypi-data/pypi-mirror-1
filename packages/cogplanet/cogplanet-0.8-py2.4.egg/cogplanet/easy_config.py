from cogplanet.model import *
from turbogears.database import session
from sqlalchemy.exceptions import InvalidRequestError
from cherrypy import config

if config.get('easy_config.enabled', True):
    try:
        planet = Planet.selectone()
    except InvalidRequestError:
        print "No planet was found.  Let's create one."
        trans = session.create_transaction()
        planet = Planet()
        print "Name your planet: ",
        planet.name = raw_input()
        trans.commit()
        print "Great, we'll never need to go over that again."

    try:
        group = Group.selectone(Group.c.group_name=='cp_admin')
    except InvalidRequestError:
        trans = session.create_transaction()
        group = Group()
        group.group_name = 'cp_admin'
        group.display_name = 'Planet Admin'
        trans.commit()

    if len(group.users) == 0:
        def set_password(user):
            from getpass import getpass
            p1 = getpass("Password: ")
            p2 = getpass("Password (Confirm): ")
            if p1 != p2:
                print "Passwords do not match, try again."
                set_password(user)
            else:
                import sha
                hash = sha.new(p1)
                user.password = hash.hexdigest()

        print "No planet administrator was found.  Let's create one."
        trans = session.create_transaction()
        user = User()
        print "Username: ",
        user.user_name = raw_input()
        print "Display Name: ",
        user.display_name = raw_input()
        print "Email: ",
        user.email_address = raw_input()
        set_password(user)
        group.users.append(user)
        trans.commit()
        print "Great, we'll never need to go over that again."
