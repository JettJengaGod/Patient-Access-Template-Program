from django.core.serializers import json
from django.http import HttpResponse


def returnhtml(request):
    return HttpResponse('this is dynamic html from db_scripts.py', content_type="application/json")
