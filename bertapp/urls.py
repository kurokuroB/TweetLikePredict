from django.contrib import admin
from django.urls import path
from .views import predictfunc, inputfunc

urlpatterns = [
    path('input/', inputfunc , name='input'),
    path('predict/',predictfunc , name='predict'),
]
