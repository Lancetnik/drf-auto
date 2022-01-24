from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend


def serializer(model, **kwargs) -> serializers.ModelSerializer:
    model_name = model._meta.object_name
    if not kwargs.get('fields'): kwargs['fields'] = "__all__"
    kwargs['model'] = model
    return type(
            model_name.replace('Model', 'Serializer'),
            (serializers.ModelSerializer,),
            {
                "Meta": type('Meta', tuple(), kwargs)
            }
        )


def filter(model, **kwargs) -> serializers.ModelSerializer:
    model_name = model._meta.object_name
    fields = {i.name for i in model._meta.fields}

    if not kwargs.get('fields'): kwargs['fields'] = "__all__"
    exclude = kwargs.get('exclude')
    if exclude: fields -= set(exclude)
    fl = kwargs.get('fields')
    if fl and fl != '__all__': fields = fields & set(fl)

    fields = {i: ['exact', 'contains'] for i in fields}
    meta = type(
            'Meta',
            tuple(), {
                "model": model,
                "fields": fields
            })
    fields = {i: filters.CharFilter() for i in fields.keys()}
    fields['Meta'] = meta
    return type(
                model_name.replace('Model', 'Filter'),
                (filters.FilterSet,),
                fields
            )


def baseView(model, **kwargs):
    model_name = model._meta.object_name
    return type(
        model_name.replace('Model', 'View'),
        (CreateAPIView,),
        {
            'queryset': model.objects.all(),
            'serializer_class': serializer(
                model,
                fields=kwargs.get('serializer_fields'),
                exclude=kwargs.get('serializer_exclude')
            ),
            'filter_backends': (DjangoFilterBackend,),
            'filterset_class': filter(
                model,
                fields=kwargs.get('filter_fields'),
                exclude=kwargs.get('filter_exclude')
            )
        }
    )