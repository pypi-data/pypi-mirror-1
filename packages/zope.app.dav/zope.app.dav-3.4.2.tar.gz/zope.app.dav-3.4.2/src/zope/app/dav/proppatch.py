##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""WebDAV method PROPPATCH

$Id: proppatch.py 85556 2008-04-21 17:53:56Z lgs $
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

import transaction
from zope.component import getUtilitiesFor, queryUtility
from zope.schema import getFieldNamesInOrder, getFields
from zope.app.container.interfaces import IReadContainer
from zope.publisher.http import status_reasons
from zope.app.form.utility import setUpWidget, no_value
from zope.traversing.browser.absoluteurl import absoluteURL

from interfaces import IDAVNamespace, IDAVWidget
from opaquenamespaces import IDAVOpaqueNamespaces

class PROPPATCH(object):
    """PROPPATCH handler for all objects"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        ct = request.getHeader('content-type', 'text/xml')
        if ';' in ct:
            parts = ct.split(';', 1)
            self.content_type = parts[0].strip().lower()
            self.content_type_params = parts[1].strip()
        else:
            self.content_type = ct.lower()
            self.content_type_params = None
        self.default_ns = 'DAV:'
        self.oprops = IDAVOpaqueNamespaces(self.context, None)

        _avail_props = {}
        # List all *registered* DAV interface namespaces and their properties
        for ns, iface in getUtilitiesFor(IDAVNamespace):
            _avail_props[ns] = getFieldNamesInOrder(iface)
        # List all opaque DAV namespaces and the properties we know of
        if self.oprops:
            for ns, oprops in self.oprops.items():
                _avail_props[ns] = list(oprops.keys())
        self.avail_props = _avail_props

    def PROPPATCH(self):
        if self.content_type not in ['text/xml', 'application/xml']:
            self.request.response.setStatus(400)
            return ''

        resource_url = absoluteURL(self.context, self.request)
        if IReadContainer.providedBy(self.context):
            resource_url += '/'

        xmldoc = minidom.parse(self.request.bodyStream)
        resp = minidom.Document()
        ms = resp.createElement('multistatus')
        ms.setAttribute('xmlns', self.default_ns)
        resp.appendChild(ms)
        ms.appendChild(resp.createElement('response'))
        ms.lastChild.appendChild(resp.createElement('href'))
        ms.lastChild.lastChild.appendChild(resp.createTextNode(resource_url))

        updateel = xmldoc.getElementsByTagNameNS(self.default_ns,
                                                 'propertyupdate')
        if not updateel:
            self.request.response.setStatus(422)
            return ''
        updates = [node for node in updateel[0].childNodes
                        if node.nodeType == node.ELEMENT_NODE and
                           node.localName in ('set', 'remove')]
        if not updates:
            self.request.response.setStatus(422)
            return ''
        self._handlePropertyUpdate(resp, updates)

        body = resp.toxml('utf-8')
        self.request.response.setResult(body)
        self.request.response.setStatus(207)
        return body

    def _handlePropertyUpdate(self, resp, updates):
        _propresults = {}
        for update in updates:
            prop = update.getElementsByTagNameNS(self.default_ns, 'prop')
            if not prop:
                continue
            for node in prop[0].childNodes:
                if not node.nodeType == node.ELEMENT_NODE:
                    continue
                if update.localName == 'set':
                    status = self._handleSet(node)
                else:
                    status = self._handleRemove(node)
                results = _propresults.setdefault(status, {})
                props = results.setdefault(node.namespaceURI, [])
                if node.localName not in props:
                    props.append(node.localName)

        if _propresults.keys() != [200]:
            # At least some props failed, abort transaction
            transaction.abort()
            # Move 200 succeeded props to the 424 status
            if _propresults.has_key(200):
                failed = _propresults.setdefault(424, {})
                for ns, props in _propresults[200].items():
                    failed_props = failed.setdefault(ns, [])
                    failed_props.extend(props)
                del _propresults[200]

        # Create the response document
        re = resp.lastChild.lastChild
        for status, results in _propresults.items():
            re.appendChild(resp.createElement('propstat'))
            prop = resp.createElement('prop')
            re.lastChild.appendChild(prop)
            count = 0
            for ns in results.keys():
                attr_name = 'a%s' % count
                if ns is not None and ns != self.default_ns:
                    count += 1
                    prop.setAttribute('xmlns:%s' % attr_name, ns)
                for p in results.get(ns, []):
                    el = resp.createElement(p)
                    prop.appendChild(el)
                    if ns is not None and ns != self.default_ns:
                        el.setAttribute('xmlns', attr_name)
            reason = status_reasons.get(status, '')
            re.lastChild.appendChild(resp.createElement('status'))
            re.lastChild.lastChild.appendChild(
                resp.createTextNode('HTTP/1.1 %d %s' % (status, reason)))

    def _handleSet(self, prop):
        ns = prop.namespaceURI
        iface = queryUtility(IDAVNamespace, ns)
        if not iface:
            # opaque DAV properties
            if self.oprops is not None:
                self.oprops.setProperty(prop)
                # Register the new available property, because we need to be
                # able to remove it again in the same request!
                props = self.avail_props.setdefault(ns, [])
                if prop.localName not in props:
                    props.append(prop.localName)
                return 200
            return 403

        if not prop.localName in self.avail_props[ns]:
            return 403 # Cannot add propeties to a registered schema

        fields = getFields(iface)
        field = fields[prop.localName]
        if field.readonly:
            return 409 # RFC 2518 specifies 409 for readonly props

        value = field.get(iface(self.context))
        if value is field.missing_value:
            value = no_value
        setUpWidget(self, prop.localName, field, IDAVWidget,
            value=value, ignoreStickyValues=True)

        widget = getattr(self, prop.localName + '_widget')
        widget.setRenderedValue(prop)

        if not widget.hasValidInput():
            return 409 # Didn't match the widget validation

        if widget.applyChanges(iface(self.context)):
            return 200

        return 422 # Field didn't accept the value

    def _handleRemove(self, prop):
        ns = prop.namespaceURI
        if not prop.localName in self.avail_props.get(ns, []):
            return 200
        iface = queryUtility(IDAVNamespace, ns)
        if not iface:
            # opaque DAV properties
            if self.oprops is None:
                return 200
            self.oprops.removeProperty(ns, prop.localName)
            return 200

        # Registered interfaces
        fields = getFields(iface)
        field = fields[prop.localName]
        if field.readonly:
            return 409 # RFC 2518 specifies 409 for readonly props

        if field.required:
            if field.default is None:
                return 409 # Clearing a required property is a conflict
            # Reset the field to the default if a value is required
            field.set(iface(self.context), field.default)
            return 200

        # Reset the field to it's defined missing_value
        field.set(iface(self.context), field.missing_value)
        return 200
