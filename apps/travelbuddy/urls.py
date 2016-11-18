from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.logreg, name = 'logreg'),
    url(r'^travels$', views.dashboard, name = 'dashboard'),
    url(r'^travels/destination/(?P<id>\d+)$', views.destination, name = 'destination'),
    url(r'^travels/add$', views.adddest, name = 'adddest'),
    url(r'^travels/validate/(?P<typelogin>(register)|(login))$', views.validate, name = 'validate'),
    url(r'^travels/jointrip/(?P<id>\d+)$', views.jointrip, name = 'jointrip'),
    url(r'^travels/createtrip$', views.createtrip, name = 'createtrip'),
	url(r'^logout$', views.logout, name = 'logout'),
]
