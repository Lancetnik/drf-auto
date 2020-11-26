from .core.file_writer import FileWriter
from .core.command import AbstractCommand
                  

class Command(AbstractCommand):
    help = 'Create serializer by model'

    m_help = 'Модель, для которой необходимо сделать сериализатор'
    a_help = 'Приложение, для моделей которого необходимо сделать сериализаторы'
    A_help = 'Создание сериализаторов для всех моделей ваших приложений'

    def write(self, model, app):
        SerializerWriter(model, app).write_model()


class SerializerWriter(FileWriter):
    def _set_params(self, app):
        self.file_path = f'{app.path}\\serializers.py'
        self.type = 'Serializer'
        self.parent = 'serializers.ModelSerializer'
        self.base_import = 'from rest_framework import serializers'