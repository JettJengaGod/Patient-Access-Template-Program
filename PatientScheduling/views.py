from django.http import HttpResponse
from django.shortcuts import render


def new_schedule(request):
    return render(request, 'new_schedule.html')


def generate_schedule(request):
    numberOfChairs = request.POST['NumberOfChairs']
    return render(request, 'generate_schedule.html')