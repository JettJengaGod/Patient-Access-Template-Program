from django.contrib import admin
from PatientScheduling.models import ChemotherapyDrug


class ChemotherapyDrugAdmin(admin.ModelAdmin):
    pass
admin.site.register(ChemotherapyDrug, ChemotherapyDrugAdmin)