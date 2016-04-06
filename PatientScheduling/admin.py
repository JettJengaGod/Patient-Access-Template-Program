from django.contrib import admin
from .models import MinMaxTime
# Register your models here.

class testAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True

admin.site.register(MinMaxTime, testAdmin)