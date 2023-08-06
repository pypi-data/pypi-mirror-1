# -*- coding: utf-8 -*-
#
# File: browser.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = '''Ramon Bartl <ramon.bartl@inquant.de>'''
__docformat__ = 'plaintext'


import logging
from zope import component

from plone.app.vocabularies.types import BAD_TYPES

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

info = logging.getLogger().info
debug = logging.getLogger().debug


class AllowTypes(BrowserView):

    template = ViewPageTemplateFile("allowtypes.pt")

    def __init__(self, context, request):
        super(AllowTypes, self).__init__(context, request)
        tools = component.queryMultiAdapter(
                (context, request), name=u"plone_tools")
        self.ttool = tools.types()

    def __call__(self):
        self.request.set('disable_border', True)

        form = self.request.form

        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None

        if submitted and not cancel_button:
            debug("Form update saved")
            self.update_settings(form)
            updated = u"Updated Type Settings"
            IStatusMessage(self.request).addStatusMessage(updated, type="info")

        if cancel_button:
            debug("Form update cancelled")
            aborted = u"No changes made"
            IStatusMessage(self.request).addStatusMessage(aborted, type="info")

        return self.template()

    @property
    def list_content_types(self):
        return [t for t in self.ttool.listContentTypes() if t not in BAD_TYPES]

    @property
    def types(self):
        for t in self.list_content_types:
            ti = self.ttool.getTypeInfo(t)
            yield dict(
                    typename = t,
                    allowed = self.allowed(t),
                    globalallow = ti.global_allow,
                    filter = ti.filter_content_types,
                    )

    def allowed(self, contentType):
        ti = self.ttool.getTypeInfo(contentType)

        for t in self.list_content_types:
            checked = t in ti.allowed_content_types

            yield dict(
                    type = t,
                    checked = checked,
                    )

    def update_settings(self, data):
        types = self.list_content_types

        for k, v in data.iteritems():
            if k not in types:
                continue

            ti = self.ttool.getTypeInfo(k)

            ti.filter_content_types = v['filter']
            debug("Set filter content types of type %s to %s"
                    % (k, ti.filter_content_types))

            ti.global_allow = v['globalallow']
            debug("Set global allow of type %s to %s"
                    % (k, ti.global_allow))

            if v.get('allowed'):
                ti.allowed_content_types = v['allowed']
                debug("Set allowed content types of type %s to %s"
                        % (k, ti.allowed_content_types))
            else:
                ti.allowed_content_types = ()
                debug("Set allowed content types of type %s to %s"
                        % (k, ti.allowed_content_types))

        return True

# vim: set ft=python ts=4 sw=4 expandtab :
