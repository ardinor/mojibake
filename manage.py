from flask.ext.script import Manager, Server, prompt_bool
from mojibake.main import app, db

manager = Manager(app)

manager.add_command('runserver', Server(
    use_debugger=True,
    use_reloader=True)
)


@manager.command
def drop():

    "Drops database tables"

    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def create():

    "Creates database tables from sqlalchemy models"

    db.create_all()


if __name__ == '__main__':
    manager.run()
