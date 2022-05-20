from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
import os

def index(request):
	seo = {
		'title': "콘디",
	}

	return render(request, 'main/index.html' ,{"seo":seo})

def robots(request):
	f = open(os.path.join(settings.BASE_DIR, 'robots.txt'), 'r')
	file_content = f.read()
	f.close()
	
	return HttpResponse(file_content, content_type="text/plain")