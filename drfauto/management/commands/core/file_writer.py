from abc import abstractmethod
import itertools

from django.apps import apps
from django.core.management.base import CommandError


class FileWriter:
    @abstractmethod
    def _set_params(self, app): pass

    @abstractmethod
    def _custom_imports(self): pass

    def __init__(self, model, app):
        self.model = model
        self.file_path = ''
        self.imports = []
        self.body = []

        self._set_params(app)
        self._split_file()
    
    def write_model(self):
        self._construct_imports()
        self.imports.append('')
        self.imports.append('')
        self._construct_body()
        with open(self.file_path, 'w') as f:
            f.write(self._as_str())

    def _as_str(self):
        strings = self.imports  + self.body
        return '\n'.join(strings)

    def _split_file(self):
        ''' разделяет на импорты и тело '''
        try:
            with open(self.file_path, 'r') as f:
                strings = [line.rstrip('\n') for line in f]
        except FileNotFoundError:
            serializers_file = open(self.file_path, 'w')
            serializers_file.close()
            strings = []

        self.body = list(
            itertools.dropwhile(
                lambda x: 'class' not in x and 'def' not in x and 'urlpatterns' not in x,
                strings
            )
        )
        if not self.body:
            self.imports = strings
        else:
            self.imports = strings[:strings.index(self.body[0])]

        if self.imports:
            # удаляем пустые строки с конца импортов
            buf = self.imports.pop()
            while not buf: 
                if self.imports:
                    buf = self.imports.pop()
                else: break
            self.imports.append(buf)

    def _construct_classname(self, newclass):
        if 'Model' in self.model._meta.object_name:
            return self.model._meta.object_name.replace('Model', newclass)
        else:
            return self.model._meta.object_name + newclass

    def _construct_classbody(self):
        self.body.append('    class Meta:')
        self.body.append(f'        model = {self.model._meta.object_name}')
        self.body.append("        fields = '__all__'")

    def _construct_body(self):
        class_name = self._construct_classname(self.type)
        class_declaration = f"class {class_name}({self.parent}):"
        if class_declaration not in self.body:
            if self.body:
                self.body.append('')
                self.body.append('')
            self.body.append(class_declaration)
            self._construct_classbody()
            
    def _check_custom_import(self, base, name):
        import_models_string = list(filter(lambda x: f'from .{base}' in x, self.imports))
        if import_models_string:
            import_models_string = import_models_string[0]
            import_models_string_words = [i.rstrip(',') for i in import_models_string.split()]
            if name not in import_models_string_words:
                self.imports[self.imports.index(import_models_string)] = import_models_string + f', {name}'
        else:
            if self.imports and self.imports[-1]:
                if not self.imports[-1].split()[1].startswith('.'):
                    self.imports.append('')
            self.imports.append(f'from .{base} import {name}')

    def _construct_imports(self):
        if not self.imports:
            for i in self.base_imports:
                self.imports.append(i)
        else:
            for base in self.base_imports:
                if base not in self.imports:
                    self.imports = [base] + self.imports
        self._custom_imports()


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