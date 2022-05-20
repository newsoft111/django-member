from django.urls import include, path
from . import views

urlpatterns = [
	path(
		"faq/",
		include(
			[
				path('', views.faq, name='FaqList'),
			]
		)
	),
	path(
		"qna/",
		include(
			[
				path('', views.qna, name='QnaList'),
			]
		)
	),
]