from django.contrib import admin
from .models import ControlSystem, ProcessTag, ProcessData, Alarm, MaintenanceSchedule


@admin.register(ControlSystem)
class ControlSystemAdmin(admin.ModelAdmin):
    list_display = ('system_id', 'system_name', 'system_type', 'status', 'location', 'operator')
    list_filter = ('system_type', 'status', 'installed_date')
    search_fields = ('system_id', 'system_name', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProcessTag)
class ProcessTagAdmin(admin.ModelAdmin):
    list_display = ('tag_name', 'control_system', 'tag_type', 'data_type', 'is_active')
    list_filter = ('control_system', 'tag_type', 'data_type', 'is_active')
    search_fields = ('tag_name', 'description')
    readonly_fields = ('created_at',)


@admin.register(ProcessData)
class ProcessDataAdmin(admin.ModelAdmin):
    list_display = ('tag', 'timestamp', 'value', 'quality')
    list_filter = ('quality', 'timestamp')
    search_fields = ('tag__tag_name',)
    readonly_fields = ('created_at',)


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('tag', 'alarm_type', 'priority', 'status', 'occurred_at', 'acknowledged_by')
    list_filter = ('alarm_type', 'priority', 'status', 'occurred_at')
    search_fields = ('tag__tag_name', 'message')
    readonly_fields = ('created_at',)


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('control_system', 'title', 'maintenance_type', 'status', 'scheduled_date', 'technician')
    list_filter = ('maintenance_type', 'status', 'scheduled_date')
    search_fields = ('title', 'control_system__system_name')
    readonly_fields = ('created_at', 'updated_at')