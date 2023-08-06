# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009 Andy Mikhailenko and contributors
#
#  This file is part of django-todoist.
#
#  django-todoist is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#


# django
from django.contrib import admin

# this app
from models import Project, Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'checked', 'due_date', 'project_id')
    list_editable = ('checked', 'project_id')
    list_filter = ('checked', 'project_id')
    search_fields = ('content',)


class TaskInline(admin.TabularInline):
    model = Task
    fields = ('content', 'checked', 'due_date')


class ProjectAdmin(admin.ModelAdmin):
    inlines = (TaskInline,)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
