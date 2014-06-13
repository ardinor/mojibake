from celery import Celery

def create_celery():
    #celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
    #    include=['mojibake.tasks.tasks'])
    #celery.conf.update(app.config)
    #TaskBase = celery.Task

    #class ContextTask(TaskBase):
    #    abstract = True
    #    def __call__(self, *args, **kwargs):
    #        with app.app_context():
    #            return TaskBase.__call__(self, *args, **kwargs)

    #celery.Task = ContextTask

    celery = Celery('mojibake.tasks', broker='amqp://guest@LP29')

    @celery.task()
    def add_together(a, b):
        return a + b

    return celery


celery = create_celery()

if __name__ == '__main__':
    celery.start()

