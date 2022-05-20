from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='Index'),
	#path('terms-of-service/', views.TermsOfService, name='TermsOfService'),
	#path('privacy/', views.Privacy, name='Privacy'),
	path('robots.txt', views.robots),
]