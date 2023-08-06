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


# python
import re

# django
from django.db.models import (BooleanField, CharField, ForeignKey, IntegerField,
                              Manager, Model, TextField)
from django.utils.translation import ugettext_lazy as _


class Project(Model):
    cache_count = IntegerField()
    collapsed = BooleanField()
    color = CharField(max_length=250)
    indent = IntegerField()
    item_order = IntegerField()
    name = CharField(max_length=250)
    user_id = IntegerField()

    class Meta:
        ordering = ('item_order',)

    def __unicode__(self):
        indent_marks = '- ' * (self.indent-1)
        return u'%s%s' % (indent_marks, todoist_format(self.name))


class TaskManager(Manager):
    def active(self, **kw):
        return self.filter(in_history=False)
    def archived(self, **kw):
        return self.filter(in_history=True)


class Task(Model):
    chains = CharField(max_length=250, null=True)  # ?!
    checked = BooleanField()
    children = CharField(max_length=50, null=True)  # '123,456,789'
    collapsed = BooleanField()
    content = TextField()
    date_string = CharField(max_length=30, blank=True)
    due_date = CharField(max_length=50, blank=True, null=True)  # 'Wed Nov 26 23:59:59 2008'
    has_notifications = BooleanField()
    in_history = BooleanField()
    indent = IntegerField()
    is_dst = CharField(max_length=1, null=True)
    item_order = IntegerField()
    labels = CharField(max_length=50) # "[]"  or  "[123, 456]"
    mm_offset = IntegerField()
    priority = IntegerField()
    project_id = ForeignKey(Project, related_name='tasks')
    user_id = IntegerField()

    objects = TaskManager()

    def __unicode__(self):
        return todoist_format(self.content)


def todoist_format(text):
    text = text.replace('\n', '<br/>')
    text = re.sub(r'^\*', '', text)
    text = re.sub(r'%\([Bb]\)\s*(.+?)%', r'<strong>\1</strong>', text)
    text = re.sub(r'%\([Ii]\)\s*(.+?)%', r'<em>\1</em>', text)
    text = re.sub(r'"(.+?)":\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\[\[gmail=(\w+)(@gmail)?,\s*(.+?)\]\]',
                  r'<a href="http://mail.google.com/?fs=1&tf=1&view=cv&search=all&shva=1&th=\1">\3 (gmail)</a>',
                  text)
    return text
