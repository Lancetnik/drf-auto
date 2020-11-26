from .core.file_writer import FileWriter
from .core.command import AbstractCommand
                  

class Command(AbstractCommand):
    help = 'Create filter by model'

    m_help = 'Модель, для которой необходимо сделать фильтр'
    a_help = 'Приложение, для моделей которого необходимо сделать фильтры'
    A_help = 'Создание фильтров для всех моделей ваших приложений'

    def write(self, model, app):
        FilterWriter(model, app).write_model()


class FilterWriter(FileWriter):
    def _set_params(self, app):
        self.file_path = f'{app.path}\\filters.py'
        self.type = 'Filter'
        self.parent = 'filters.FilterSet'
        self.base_import = 'from django_filters import rest_framework as filters'