from flask.ext.script import Manager, Server
from mojibake import app

manager = Manager(app)

manager.add_command('runserver', Server(
    use_debugger=True,
    use_reloader=True)
)

if __name__ == '__main__':
    manager.run()
