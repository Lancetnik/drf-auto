from pathlib import Path

from .core.file_writer import FileWriter
from .core.command import AbstractCommand
from .core.urlwriter import UrlsWriter
from .makeserializer import SerializerWriter
from .makefilter import FilterWriter


class Command(AbstractCommand):
    help = 'Create filter by model'

    m_help = 'Модель, для которой необходимо сделать view'
    a_help = 'Приложение, для моделей которого необходимо сделать views'
    A_help = 'Создание views для всех моделей ваших приложений'

    def write(self, model_class, app_class, **options):
        FilterWriter(model_class, app_class).write_model()
        SerializerWriter(model_class, app_class).write_model()
        if not(options.get('create') or options.get('retrieve') or options.get('update') or
            options.get('destroy') or options.get('list') or options.get('list_create') or
            options.get('retrieve_update') or options.get('retrieve_destroy') or options.get('retrieve_update_destroy')):
                for i in options.keys():
                    options[i] = True
        if options.get('create'): CWriter(model_class, app_class).write_model()
        if options.get('retrieve'): RWriter(model_class, app_class).write_model()
        if options.get('update'): UWriter(model_class, app_class).write_model()
        if options.get('destroy'): DWriter(model_class, app_class).write_model()
        if options.get('list'): LWriter(model_class, app_class).write_model()
        if options.get('list_create'): LCWriter(model_class, app_class).write_model()
        if options.get('retrieve_update'): RUWriter(model_class, app_class).write_model()
        if options.get('retrieve_destroy'): RDWriter(model_class, app_class).write_model()
        if options.get('retrieve_update_destroy'): RUDWriter(model_class, app_class).write_model()
        UrlsWriter(model_class, app_class).write_model()
    
    def add_parser(self, parser):
        parser.add_argument('-r', '--retrieve', action='store_true', help='Создать RetrieveAPIView')
        parser.add_argument('-c', '--create', action='store_true', help='Создать CreateAPIView')
        parser.add_argument('-l', '--list', action='store_true', help='Создать ListAPIView')
        parser.add_argument('-d', '--destroy', action='store_true', help='Создать DestroyAPIView')
        parser.add_argument('-u', '--update', action='store_true', help='Создать UpdateAPIView')
        parser.add_argument('-lc', '--list-create', action='store_true', help='Создать ListCreateAPIView')
        parser.add_argument('-ru', '--retrieve-update', action='store_true', help='Создать RetrieveUpdateAPIView')
        parser.add_argument('-rd', '--retrieve-destroy', action='store_true', help='Создать RetrieveDestroyAPIView')
        parser.add_argument('-rud', '--retrieve-update-destroy', action='store_true', help='Создать RetrieveUpdateDestroyAPIView')


class ViewWriter(FileWriter):
    def _set_params(self, app):
        self.file_path = Path(app.path) / 'views.py'
        self.base_imports = [
            'from rest_framework import generics',
            'from django_filters.rest_framework import DjangoFilterBackend'
        ]

    def _custom_imports(self):
        self._check_custom_import('models', self.model._meta.object_name)
        self._check_custom_import('serializers', self._construct_classname('Serializer')) 
        self._check_custom_import('filters', self._construct_classname('Filter')) 
        
    def _construct_classbody(self):
        self.body.append(f'    queryset = {self.model._meta.object_name}.objects.all()')
        serializer_name = self._construct_classname('Serializer')
        self.body.append(f'    serializer_class = {serializer_name}')
        self.body.append(f'    filter_backends = (DjangoFilterBackend,)')
        filter_name = self._construct_classname('Filter')
        self.body.append(f'    filterset_class = {filter_name}')


class CWriter(ViewWriter):
    type = 'CreateView'
    parent = 'generics.CreateAPIView'

class RWriter(ViewWriter):
    type = 'RetrieveView'
    parent = 'generics.RetrieveAPIView'

class UWriter(ViewWriter):
    type = 'UpdateView'
    parent = 'generics.UpdateAPIView'

class DWriter(ViewWriter):
    type = 'DestroyView'
    parent = 'generics.DestroyAPIView'

class LWriter(ViewWriter):
    type = 'ListView'
    parent = 'generics.ListAPIView'

class LCWriter(ViewWriter):
    type = 'ListCreateView'
    parent = 'generics.ListCreateAPIView'

class RUWriter(ViewWriter):
    type = 'RetrieveUpdateView'
    parent = 'generics.RetrieveUpdateAPIView'

class RDWriter(ViewWriter):
    type = 'RetrieveDestroyView'
    parent = 'generics.RetrieveDestroyAPIView'

class RUDWriter(ViewWriter):
    type = 'RetrieveUpdateDestroyView'
    parent = 'generics.RetrieveUpdateDestroyAPIView'