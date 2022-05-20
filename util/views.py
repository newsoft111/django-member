from django.shortcuts import render
from django.core.mail import EmailMessage
from account.models import UserPoint
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.base import ContentFile
import os
from io import BytesIO
from PIL import Image as PilImage
# Create your views here.
import re

def EmailSender(email, subject, message, mailType):
	if email is not None:
			subject = subject
			message = message
			mail = EmailMessage(subject, message, to=[email])
			if mailType is not None:
				mail.content_subtype = mailType
			mail.send()
			result = '200'
	else:
			result = '201'
	return result


def AddUserPointLog(user, place, amount):
	amount = int(re.sub(r'[^0-9]', '', str(amount)))
	try:
		user.point = user.point + amount
		user.save()

		result = True
	except:
		result = False
	
	if result:
		point_log = UserPoint() #포인트 내역 추가
		point_log.user = user
		point_log.place = place
		point_log.amount = amount
		point_log.save()
	return result