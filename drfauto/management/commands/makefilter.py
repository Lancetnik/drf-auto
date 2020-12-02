from .core.file_writer import FileWriter
from .core.command import AbstractCommand
                  

class Command(AbstractCommand):
    help = 'Create filter by model'

    m_help = 'Модель, для которой необходимо сделать фильтр'
    a_help = 'Приложение, для моделей которого необходимо сделать фильтры'
    A_help = 'Создание фильтров для всех моделей ваших приложений'

    def write(self, model_class, app_class, **options):
        FilterWriter(model_class, app_class).write_model()


class FilterWriter(FileWriter):
    def _set_params(self, app):
        self.file_path = f'{app.path}\\filters.py'
        self.type = 'Filter'
        self.parent = 'filters.FilterSet'
        self.base_imports = ['from django_filters import rest_framework as filters']
    
    def _custom_imports(self):
        self._check_custom_import('models', self.model._meta.object_name)