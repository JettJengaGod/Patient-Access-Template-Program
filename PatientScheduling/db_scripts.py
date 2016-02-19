import json
from django.http import HttpResponse


def returnhtml(request):
    html = "saved: "
    for key in request.GET:
        html += key + " " + request.GET[key] + ", "
    return HttpResponse(html, content_type="application/json")
