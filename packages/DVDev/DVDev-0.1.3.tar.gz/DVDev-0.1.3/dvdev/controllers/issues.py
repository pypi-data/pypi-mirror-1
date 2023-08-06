# DVDev - Distributed Versioned Development - tools for Open Source Software
# Copyright (C) 2009  Douglas Mayle

# This file is part of DVDev.

# DVDev is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# DVDev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with DVDev.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to, redirect
from pylons.decorators import rest
from pylons.decorators import jsonify

from dvdev.lib.base import BaseController, render

import yamltrak
from pylons import config
from os import path

repositories = dict((repo.split(path.sep)[-1], repo) for repo in config.get('repo').split())

log = logging.getLogger(__name__)

class IssuesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('issue', 'issues')

    def index(self, repository, format='html'):
        """GET /issues: All items in the collection"""
        # url('issues')
        # Read the config to find the repository source...
        # Need to figure out the ini file, the issues directory
        # I think YAMLTrak should be a package, not a webapp...
        allissues = yamltrak.issues(repositories.values(), 'issues')
        c.issues = {}
        for repo in repositories:
            c.issues[repo] = {}
            issuedb = allissues.get(repo, {})
            for issueid, issue in issuedb.iteritems():
                group = issue.get('group', 'unfiled')
                c.issues[repo][group] = c.issues[repo].get(group, {})
                c.issues[repo][group][issueid] = issue
            if repo not in allissues:
                c.issues[repo] = None
                
        return render('issues/index.html')

    def create(self, repository):
        """POST /issues: Create a new item"""
        # url('issues')

    @rest.dispatch_on(POST='_add_new')
    def new(self, repository, format='html'):
        """GET /issues/new: Form to create a new item"""
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'newticket', detail=False)
        if not skeleton:
            # If there is no newticket skeleton, just use the default skeleton.
            skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        c.skeleton = skeleton[0]['data']
        keys = c.skeleton.keys()
        orderedkeys = []
        if 'title' in keys:
            keys.remove('title')
            orderedkeys.append('title')
        if 'description' in keys:
            keys.remove('description')
            orderedkeys.append('description')
        orderedkeys += keys
        c.orderedkeys = orderedkeys
        
        return render('issues/add.html')
        # url('new_issue')

    def _add_new(self, repository, format='html'):
        issue = {}
        issue['title'] = request.params.get('title')
        issue['description'] = request.params.get('description')
        issue['estimate'] = request.params.get('estimate')
        if not issue['title'] or not issue['description'] or not 'estimate' in request.params:
            c.issue = issue
            return render('issues/add.html')
        issueid = yamltrak.new(repositories[repository], issue)
        url = request.environ['routes.url']
        redirect(url.current(repository=repository, id=issueid, action='show'))

    def update(self, repository, id):
        """PUT /issues/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('issue', id=ID),
        #           method='put')
        # url('issue', id=ID)

    def delete(self, repository, id):
        """DELETE /issues/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('issue', id=ID),
        #           method='delete')
        # url('issue', id=ID)

    def close(self, repository, id):
        """POST /issues/id: Show a specific item"""
        # url('issue', id=ID)
        if yamltrak.close(repositories[repository], id):
            redirect_to('/issues')
        redirect_to(action='show', id=id)

    def show(self, repository, id, format='html'):
        """GET /repository/issues/id: Show a specific item"""
        # url('issue', id=ID)
        c.id = id
        issue = yamltrak.issue(repositories[repository], 'issues', id)
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        c.issue = issue[0]['data']
        c.skeleton = skeleton[0]['data']
        c.uncommitted_diff = issue[0].get('diff')
        c.versions = issue[1:]
        return render('issues/issue.html')

    def initialize(self, repository, format='html'):
        """GET /issues/id/edit: Form to edit an existing item"""

        url = request.environ['routes.url']

        yamltrak.dbinit(repository)
        return redirect(url(controller='issues', repository=repository, action='index'))

    @rest.dispatch_on(GET='show')
    def edit(self, repository, id, format='html'):
        """GET /issues/id/edit: Form to edit an existing item"""
        # In order to to properly handle partial completion, we'll start by
        # filling out any features from the existing ticket if the key is in
        # the skeleton.  Next we fill in any fields from the skeleton not in
        # the ticket with the default values.  Finally, for each value in the
        # request that has a corresponding key in the skeleton, we'll update
        # the ticket.
        oldissue = yamltrak.issue(repositories[repository], 'issues',id, detail=False)
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        newissue = {}
        for key in skeleton[0]['data']:
            if key in oldissue[0]['data']:
                newissue[key] = oldissue[0]['data'][key]
            else:
                newissue[key] = skeleton[0]['data'][key]
            if key in request.params:
                newissue[key] = request.params[key]
        yamltrak.edit_issue(repositories[repository], 'issues', newissue, id)
        redirect_to(action='show', id=id)

    def burndown(self, repository, id):
        c.group = id
        c.groupdata = yamltrak.burndown(repository, id)
        # Find the max point.  Find the most recent if multiple are the same.
        # Using that point as a base, find the point going forward that gives
        # the greatest slope.
        maxtime = None
        maxwork = 0
        worstslope = 0
        for timestamp, workleft in c.groupdata:
            if workleft >= maxwork:
                maxtime, maxwork = timestamp, workleft
        for timestamp, workleft in c.groupdata:
            try:
                if (timestamp - maxtime) / (workleft - maxwork) < worstslope:
                    worstslope = (timestamp - maxtime) / (workleft - maxwork)
            except ZeroDivisionError:
                pass


        c.maxtime = maxtime
        c.maxwork = maxwork
        c.worsttime = -worstslope * maxwork + maxtime

        # With these two points, find the third on the line at the zero point.
        return render('issues/burndown.html')
