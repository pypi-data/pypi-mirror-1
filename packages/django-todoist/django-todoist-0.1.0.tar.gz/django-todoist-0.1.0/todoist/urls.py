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


from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('todoist.views',
    url('^$', 'overview',
        name='todoist-overview'),
    url('^projects/$', 'project_list',
        name='todoist-project-list'),
    url('^projects/(?P<project_id>\d+)/$', 'project_detail',
        name='todoist-project-detail'),
    url('^tasks/$', 'task_list',
        name='todoist-task-list'),
)
