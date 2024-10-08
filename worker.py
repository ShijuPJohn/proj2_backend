from celery import Celery, Task


def celery_init_app(app) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object('celery_config')
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

# celery -A app.celery_app worker -l info
# celery -A app.celery_app beat --max-interval=1 -l info
