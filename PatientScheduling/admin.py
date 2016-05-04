from django.conf import settings
from django.contrib import admin
from PatientScheduling.models import ChemotherapyDrug, NurseScheduleGroups, SavedTimeSlot


class ChemotherapyDrugAdmin(admin.ModelAdmin):
    list_display = ('Name',)
    ordering = ('Name',) # sort alphabetically by name


class RNScheduleAdmin(admin.ModelAdmin):
    list_display = ('Name','SavedDate')
    ordering = ('SavedDate',)
    exclude = ('UserCreated', 'Chairs')

    def get_queryset(self, request):
        # qs = super(RNScheduleAdmin, self).get_queryset(request)
        qs = NurseScheduleGroups.objects.filter(UserCreated=True)
        return qs
    def has_add_permission(self, request):
        return False


class TimeSlotGroupAdmin(admin.ModelAdmin):
    list_display = ('Name','SavedDate')
    fields = ('Name',)

    def get_queryset(self, request):
        # qs = super(RNScheduleAdmin, self).get_queryset(request)
        qs = SavedTimeSlot.objects.all().distinct('Name')
        return qs
    def has_add_permission(self, request):
        return False
    def delete_model(self, request, obj):
        SavedTimeSlot.objects.filter(Name=obj.Name).delete()


admin.site.register(ChemotherapyDrug, ChemotherapyDrugAdmin)
admin.site.register(NurseScheduleGroups, RNScheduleAdmin)
admin.site.register(SavedTimeSlot, TimeSlotGroupAdmin)
