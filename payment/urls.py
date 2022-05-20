from django.urls import path, include
from . import views

urlpatterns = [
	path(
		"campaign/",
		include(
			[
				path('check/', views.campaign_payment_check, name='CampaignPaymentCheck'),
			]
		)
	),
]
