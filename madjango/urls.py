from django.conf.urls import patterns, url

from .views import api

urlpatterns = patterns('',
    url(r'^$',api, name='madjango.product.search')
)
