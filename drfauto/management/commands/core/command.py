from abc import abstractmethod

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

from .file_writer import find_model_by_name, find_models_by_appname


class AbstractCommand(BaseCommand):
    @abstractmethod
    def write(self, model, app): pass

    def add_parser(self, parser): pass

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', type=str, help=self.m_help)
        parser.add_argument('-a', '--app', type=str, help=self.a_help)
        parser.add_argument('-A', '--all', action='store_true', help=self.A_help)
        self.add_parser(parser)

    def handle(self, *app_labels, **options):
        model = options.get('model')
        app = options.get('app')
        all_apps = options.get('all')
        if model:
            f = find_model_by_name(model)
            model, app = f.get('model'), f.get('app')
            self.write(model, app, **options)
            return
        elif app:
            f = find_models_by_appname(app)
            models, app = f.get('models'), f.get('app')
            for model in models:
                self.write(model, app, **options)
            return
        elif all_apps:
            my_apps = list(filter(lambda x: 'lib' not in x.path, apps.get_app_configs()))
            for app in my_apps:
                f = find_models_by_appname(app.label)
                models, app = f.get('models'), f.get('app')
                for model in models:
                    self.write(model, app, **options)
            return
        else:
            raise CommandError('Needs to point\n\
[-a] [--app] "app_name" to create serializers for all app`s models\n\
[-m] [--molel] "model_name" to create serializer for this model\n\
[-A] [--all] to create serializers for all models in your apps')