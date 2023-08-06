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
from django.shortcuts import get_list_or_404, get_object_or_404

# 3rd-party
from view_shortcuts.decorators import render_to

# this app
from models import Project, Task

@render_to()
def overview(request):
    return {}

@render_to()
def project_list(request):
    object_list = get_list_or_404(Project)
    return {'object_list': object_list}

@render_to()
def project_detail(request, project_id):
    obj = get_object_or_404(Project, pk=project_id)
    return {'object': obj}

@render_to()
def task_list(request):
    object_list = Task.objects.all()
    return {'object_list': object_list}
