from django.http import HttpResponse
from django.shortcuts import render


def new_schedule(request):
    return render(request, 'new_schedule.html')


