from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm


def new_schedule(request):
    if request.method == 'POST':  # if this is a POST request we need to process the form data
        chairsForm = ChairsForm(request.POST)
        RNform = RNFormSet(request.POST, prefix='RN')
        Appform = AppointmentFormSet(request.POST, prefix='APP')
        if RNform.is_valid() & Appform.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/generateSchedule/')
    else:  # if a GET (or any other method) we'll create a blank form
        chairsForm = ChairsForm()
        RNform = RNFormSet(prefix='RN')
        Appform = AppointmentFormSet(prefix='APP')
    context = {'RNFormSet': RNform, 'AppointmentFormSet': Appform, 'ChairsForm': chairsForm}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'generate_schedule.html')
