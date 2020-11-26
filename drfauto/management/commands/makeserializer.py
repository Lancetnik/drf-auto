import itertools

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import models

from loguru import logger


class Command(BaseCommand):
    help = 'Create serializer by model'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', type=str, help='Модель, для которой необходимо сделать сериализатор')
        parser.add_argument('-a', '--app', type=str, help='Приложение, для моделей которого необходимо сделать сериализаторы')
        parser.add_argument('-A', '--all', action='store_true', help='Создание сериализаторов для всех моделей ваших приложений')

    def handle(self, *app_labels, **options):
        model = options.get('model')
        app = options.get('app')
        all_apps = options.get('all')
        if model:
            f = _find_model_by_name(model)
            model, app = f.get('model'), f.get('app')
            _write_model(model, app)
            return
        elif app:
            f = _find_models_by_appname(app)
            models, app = f.get('models'), f.get('app')
            for model in models:
                _write_model(model, app)
            return
        elif all_apps:
            my_apps = list(filter(lambda x: 'lib' not in x.path, apps.get_app_configs()))
            for app in my_apps:
                f = _find_models_by_appname(app.label)
                models, app = f.get('models'), f.get('app')
                for model in models:
                    _write_model(model, app)
            return
        else:
            raise CommandError('Needs to point\n\
[-a] [--app] "app_name" to create serializers for all app`s models\n\
[-m] [--molel] "model_name" to create serializer for this model\n\
[-A] [--all] to create serializers for all models in your apps')
                  

class SerializerWriter:
    def __init__(self, model, app):
        self.model = model
        self.serializers_path = f'{app.path}\\serializers.py'

        self.strings = []

    def as_str(self):
        return ''.join(self.strings)

    def write_serializer(self):
        with open(self.serializers_path, 'r') as f:
            strings = [line for line in f][3:]
        serializer_name = self.model._meta.object_name.replace('Model', 'Serializer')
        serializer_declaration = f"class {serializer_name}(serializers.ModelSerializer):\n"
        if serializer_declaration not in strings:
            self.strings.append('\n')
            self.strings.append('\n')
            self.strings.append(f"{serializer_declaration}\
    class Meta:\n\
        model = {self.model._meta.object_name}\n\
        fields = '__all__'")

    def write_imports(self):
        try: 
            serializers_file = open(self.serializers_path, 'r')
        except FileNotFoundError:
            serializers_file = open(self.serializers_path, 'w')
            serializers_file.close()
            self.strings.append('from rest_framework import serializers\n')
            self.strings.append('\n')
            self.strings.append(f'from .models import {self.model._meta.object_name}\n')
        else:
            strings = list(itertools.dropwhile(lambda x: 'class' in x, [line for line in serializers_file]))
            serializers_file.close()

            if 'from rest_framework import serializers\n' not in strings:
                self.strings.append('from rest_framework import serializers\n')
                self.strings.append('\n')
            self.strings.extend(strings)

            import_models_string = list(filter(lambda x: 'from .models' in x, strings))
            if import_models_string:
                import_models_string = import_models_string[0]
                import_models_string_words = [i.rstrip(',') for i in import_models_string.split()]
                if self.model._meta.object_name not in import_models_string_words:
                    self.strings[self.strings.index(import_models_string)] = import_models_string.replace('\n', f', {self.model._meta.object_name}\n')
            else: self.strings.append(f'from .models import {self.model._meta.object_name}\n')


def _find_model_by_name(modelname: str) -> dict:
    my_apps = apps.get_app_configs()
    my_apps = list(filter(lambda x: 'lib' not in x.path, my_apps))
    for app_label in my_apps:
        for model in app_label.get_models():
            if model._meta.object_name == modelname:
                return {
                    'model': model,
                    'app': app_label
                }
    apps_list = ', '.join([i.label for i in my_apps])
    raise CommandError(f"Model '{modelname}' not found\nIn apps: {apps_list}")

def _find_models_by_appname(appname: str) -> dict:
    my_apps = apps.get_app_configs()
    my_app = list(filter(lambda x: x.label==appname, my_apps))
    if not my_app:
        raise CommandError(f"Model '{appname}' not found")
    else:
        my_app = my_app[0]

    return {
        'models': list(my_app.get_models()),
        'app': my_app
    }

def _write_model(model, app):
    writer = SerializerWriter(model, app)
    writer.write_imports()
    writer.write_serializer()

    with open(f'{app.path}\\serializers.py', 'w') as f:
        f.write(writer.as_str())