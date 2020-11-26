from abc import abstractmethod
import itertools

from django.apps import apps
from django.core.management.base import CommandError


class FileWriter:
    @abstractmethod
    def _set_params(self, app): pass

    def __init__(self, model, app):
        self.model = model
        self.file_path = ''
        self.imports = []
        self.body = []

        self._set_params(app)
        self._split_file()

    
    def write_model(self):
        self._construct_imports()
        self._construct_body()
        with open(self.file_path, 'w') as f:
            f.write(self._as_str())

    def _as_str(self):
        strings = self.imports + self.body
        return '\n'.join(strings)

    def _split_file(self):
        try:
            with open(self.file_path, 'r') as f:
                strings = [line.rstrip('\n') for line in f]
        except FileNotFoundError:
            serializers_file = open(self.file_path, 'w')
            serializers_file.close()
            strings = []

        self.body = list(
            itertools.dropwhile(
                lambda x: 'class' not in x and 'def' not in x,
                strings
            )
        )
        if not self.body:
            self.imports = strings
        else:
            self.imports = strings[:strings.index(self.body[0])]

    def _construct_body(self):
        class_name = self.model._meta.object_name.replace('Model', self.type)
        class_declaration = f"class {class_name}({self.parent}):"
        if class_declaration not in self.body:
            self.body.append('')
            self.body.append('')
            self.body.append(class_declaration)
            self.body.append('    class Meta:')
            self.body.append(f'        model = {self.model._meta.object_name}')
            self.body.append("        fields = '__all__'")

    def _construct_imports(self):
        if not self.imports:
            self.imports.append(self.base_import)
            self.imports.append('')
            self.imports.append(f'from .models import {self.model._meta.object_name}')
        else:
            if self.base_import not in self.imports:
                self.imports = [self.base_import, ''] + self.imports

            import_models_string = list(filter(lambda x: 'from .models' in x, self.imports))
            if import_models_string:
                import_models_string = import_models_string[0]
                import_models_string_words = [i.rstrip(',') for i in import_models_string.split()]
                if self.model._meta.object_name not in import_models_string_words:
                    self.imports[self.imports.index(import_models_string)] = import_models_string + f', {self.model._meta.object_name}'
            else: self.imports.append(f'from .models import {self.model._meta.object_name}')



def find_model_by_name(modelname: str) -> dict:
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

def find_models_by_appname(appname: str) -> dict:
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