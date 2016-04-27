"""ECS193 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import PatientScheduling.db_scripts
import PatientScheduling.views

urlpatterns = [
    url(r'^$', PatientScheduling.views.home),
    url(r'^admin/', admin.site.urls),
    url(r'^settings/', PatientScheduling.views.settings_page),
    url(r'^newSchedule/', PatientScheduling.views.new_schedule),
    url(r'^home/', PatientScheduling.views.home),
    url(r'^savedschedules/', PatientScheduling.views.saved_schedules),
    url(r'^viewschedule/(?P<schedule_id>\d+)', PatientScheduling.views.view_schedule),
    # scripts called from ajax on newSchedule page
    url(r'^add_to_schedule_group/', PatientScheduling.db_scripts.add_to_schedule_group),
    url(r'^load_schedule_group/', PatientScheduling.db_scripts.load_schedule_group),
    url(r'^check_schedule_group_name/', PatientScheduling.db_scripts.check_schedule_group_name),
    url(r'^load_schedule_group_names/', PatientScheduling.db_scripts.load_schedule_group_names),
    url(r'^delete_schedule_group/', PatientScheduling.db_scripts.delete_schedule_group),
    # scripts called from ajax on calendar page
    url(r'^remove_schedule/', PatientScheduling.db_scripts.remove_schedule),
    url(r'^save_schedule/', PatientScheduling.db_scripts.save_schedule),
    url(r'^check_schedule_name/', PatientScheduling.db_scripts.check_schedule_name),
    # for saving and loading time slots
    url(r'^save_time_slot/', PatientScheduling.db_scripts.save_time_slot),
    url(r'^delete_time_slot/', PatientScheduling.db_scripts.delete_time_slot),
    url(r'^check_time_slot_group_name/', PatientScheduling.db_scripts.check_time_slot_group_name),
    url(r'^load_time_slot_group/', PatientScheduling.db_scripts.load_time_slot_group),
    url(r'^load_time_slot_group_names/', PatientScheduling.db_scripts.load_time_slot_group_names)
                    #also need a load all unique save names
]
