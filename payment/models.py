from django.db import models
from django.conf import settings
from datetime import datetime

class Payment(models.Model):
	user = models.ForeignKey(
				settings.AUTH_USER_MODEL,
				on_delete=models.CASCADE
	)
	pay_method = models.CharField(max_length=255)
	pg = models.CharField(max_length=255)
	paid_amount = models.IntegerField()
	paid_at = models.DateTimeField(default=datetime.now)
	merchant_uid = models.CharField(max_length=255,unique=True)
	imp_uid = models.CharField(max_length=255)
	apply_num = models.CharField(max_length=255)
	is_refund=models.BooleanField(default=False)

	class Meta:
		managed = True
		db_table = 'payment'