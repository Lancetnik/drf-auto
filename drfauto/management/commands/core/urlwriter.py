from re import finditer

from .file_writer import FileWriter


class UrlsWriter(FileWriter):
    def _set_params(self, app):
        self.file_path = f'{app.path}\\urls.py'
        self.base_imports = [
            'from django.urls import path',
        ]
    
    def _custom_imports(self):
        self._check_custom_import('', 'views')

    def _construct_paths(self):
        with open(self.file_path.replace('urls', 'views')) as f:
            views = [camel_case_split(line.split('(')[0].split()[1]) for line in f if line.startswith('class')]
            return [ViewConstructor(i).to_path() for i in views]
                
    def _construct_body(self):
        if len(self.body) == 1:
            self.body = ['urlpatterns = [']
            self.body += self._construct_paths()
            self.body.append(']')
        else:
            paths = list(filter(lambda x: x.startswith('    path'), self.body))
            if not paths:
                self.body = ['']
                self._construct_body()
            else:
                self.body = ['urlpatterns = [']
                self.body += sorted(list(set(paths) | set(self._construct_paths())))
                self.body.append(']')


class ViewConstructor:
    views = ['List', 'Create', 'Retrieve', 'Update', 'Destroy'] # order is important

    def __init__(self, words: list):
        self.viewtype = ''
        for view in self.views:
            if view in words:
                self.viewtype += view
                words.remove(view)
        words.remove('View')
        self.classname = ''.join(words)

    def __str__(self):
        return f'{self.classname} : {self.viewtype}'

    def __repr__(self):
        return f'{self.classname} : {self.viewtype}'

    def to_path(self):
        if 'retrieve' in self.viewtype.lower() or 'update' in self.viewtype.lower() or 'destroy' in self.viewtype.lower():
            return f'    path("{self.classname.lower()}/{self.viewtype.lower()}/<int:pk>/", views.{self.classname}{self.viewtype}View.as_view()),'
        else:
            return f'    path("{self.classname.lower()}/{self.viewtype.lower()}/", views.{self.classname}{self.viewtype}View.as_view()),'


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z0123456789])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z0123456789])|$)', identifier)
    return [m.group(0) for m in matches]