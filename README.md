# Django Rest Framework auto creator
### Creates serializers, filters and generics for created model

Installation: `pip install drfauto`

Include `drf_auto` into Django `Installed apps` and use 
`python manage.py makeserializer | makefilter | makeviews` for your `-m model_name` or `-a app_name` or `-A` all project. This commands generate serializers.py, filters.py and views.py in your apps directories and create suitable classes.
Also u can import `drf_auto.dynamic` for creating class as python object in your code. This classes can be used as abstract for inheritance or ready functional classes.