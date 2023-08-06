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


"Todoist API"


import httplib2
import urllib

try:
    import simplejson as json
except ImportError:
    import json


class ConnectionError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class TodoistClient(object):
    def __init__(self, email, password):
        self._http = httplib2.Http('.cache')
        self.user_data = None
        self._login(email, password)

    #
    # PYTHON MAGIC METHODS
    #

    def __repr__(self):
        return u'<TodoistClient %s>' % self.user_data['email']

    #
    # INTERNAL METHODS
    #

    def _call(self, cmd, **kw):
        if not 'token' in kw:
            kw.update({'token': self.user_data['api_token']})
        url = u'http://todoist.com/API/%s?%s' % (cmd, urllib.urlencode(kw))
        response, content = self._http.request(url)
        if not response['status'] == '200':
            raise ConnectionError('%s failed: unexpected response status %s for URL %s'
                                  % (cmd, response['status'], url))
        return json.loads(content)

    def _login(self, email, password):
        data = self._call('login', email=email, password=password, token='')
        if data == 'LOGIN_ERROR':
            raise AuthenticationError('login error')
        self.user_data = data

    #
    # PUBLIC METHODS
    #

    def get_projects(self):
        return self._call('getProjects')

    def get_project(self, project_id):
        return self._call('getProject', project_id=project_id)

    def get_open_tasks(self, project_id):
        return self._call('getUncompletedItems', project_id=project_id)

    def get_closed_tasks(self, project_id):
        return self._call('getCompletedItems', project_id=project_id)

    def get_tasks(self, project_id):
        for x in self.get_open_tasks(project_id):
            yield x
        for x in self.get_closed_tasks(project_id):
            yield x

    def get_items_by_ids(self, ids):
        assert hasattr(ids, '__iter__'), 'expected an iterable'
        return self._call('getItemsById', ids=ids)
