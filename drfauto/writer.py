import copy
from itertools import dropwhile
import traceback

from django.apps import apps

from .management.commands.makeserializer import Command as Scommand
from .management.commands.makefilter import Command as Fcommand
from .management.commands.makeview import Command as Vcommand


def makeserializer(model=None, clear=False):
    _make(Scommand(), model, clear)

def makefilter(model=None, clear=False):
    _make(Fcommand(), model, clear)

def makeview(model=None, tags=[], clear=False):
    options = dict()
    options['create'] = 'c' in tags
    options['retrieve'] = 'r' in tags
    options['update'] = 'u' in tags
    options['destroy'] = 'd' in tags
    options['list'] = 'l' in tags
    options['list_create'] = 'lc' in tags
    options['retrieve_update'] = 'ru' in tags
    options['retrieve_destroy'] = 'rd' in tags
    options['retrieve_update_destroy'] = 'rud' in tags
    _make(Vcommand(), model, clear, options)

def makeall(clear=False):
    Scommand().handle(all=True)
    Fcommand().handle(all=True)
    Vcommand().handle(all=True)
    if clear: _clear(_catch_call())

def _catch_call():
    # получаем пути файлов из стека вызовов
    trace = traceback.StackSummary.extract(traceback.walk_stack(None))
    # текущий файл
    cur_dir = trace[0].filename
    # отсеиваем все вызовы из этого файла и берем первый снаружи
    called_from = list(dropwhile(lambda x: x.filename in cur_dir, trace))[0]
    return called_from

def _clear(file):
    path = file.filename
    line = file.line
    with open(path, "r") as f:
        content = f.read().replace(f'{line}', '')
    with open(path, "w") as f:
        f.write(content)

def _make(executor, model=None, clear=False, tags=dict()):
    called_from = _catch_call()
    if clear: _clear(called_from)
    if model:
        executor.handle(model=model._meta.object_name, **tags)
    else:
        # ищем django приложение, откуда были вызваны функции из этого модуля
        app = list(filter(lambda x: x.path in called_from.filename, apps.get_app_configs()))[0].name
        executor.handle(app=app, **tags)
    
        