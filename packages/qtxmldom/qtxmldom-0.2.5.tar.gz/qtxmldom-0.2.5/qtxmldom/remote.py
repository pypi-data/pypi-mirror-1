#!/usr/bin/env python

"""
Access to remote documents via browsers and KHTML parts.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file LICENCE.txt
If not, write to the Free Software Foundation, Inc.,
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

--------

Use the get_konqueror_instances function to find all instances of Konqueror
browsers which can be contacted. Each instance has a get_parts method which can
be used to discover sources of document information. Each part can be queried
for the URL of the document it is currently displaying (using the getURL method)
and the remote document itself (using the getDocument method).

Upon obtaining a remote document, use the fromRemoteNode function from qtxmldom.
The following code to get a PyXML-style DOM document from a browser:

  import qtxmldom, qtxmldom.remote
  browsers = qtxmldom.remote.get_konqueror_instances()
  parts = browsers[0].get_parts()
  remote_document = parts[0].getDocument()
  doc = qtxmldom.fromRemoteNode(remote_document)
"""

from kdecore import KApplication
import dcopext

# Node implementations.

class RemoteNode(object):

    "A representation of a remote node, accessed via DCOP."

    def __init__(self, obj, accessor):
        self.obj = obj
        self.accessor = accessor

    def __getattr__(self, name):
        return RemoteMethod(self.obj, self.accessor, name)

class RemoteMethod(object):

    """
    A wrapper around a remote method call, ensuring that the correct result is
    obtained.
    """

    def __init__(self, obj, accessor, name):
        import qt
        self.qt = qt
        self.obj = obj
        self.accessor = accessor
        self.name = name

    def _convert_obj(self, obj):
        if isinstance(obj, RemoteNode):
            return obj.obj
        else:
            return obj

    def __call__(self, *args):
        method = getattr(self.accessor, self.name)

        # Add the method's context and convert other arguments if appropriate.

        args = (self.obj,) + tuple(map(self._convert_obj, args))

        # Test the status.

        status, result_list = method(*args)
        if not status:
            raise RuntimeError, "Remote method '%s' failed for node '%s'" % (self.name, self.obj)

        if isinstance(result_list, self.qt.QStringList):
            result_type = result_list[0]
            result_value = result_list[1]
            if result_type == "string":
                return result_value
            else:
                return RemoteNode(result_value, self.accessor)
        else:
            return result_list

# Utility functions.

def get_client():

    "Return the DCOP client object."

    app = KApplication.kApplication()
    if app is None:
        raise RuntimeError, "No KApplication initialised."
    return app.dcopClient()

def get_konqueror_instances():

    "Return a list of Konqueror instances."

    client = get_client()
    app_names = map(str, client.registeredApplications())
    konq_instances = []
    for app_name in app_names:
        if app_name.startswith("konqueror"):
            konq_instances.append(Konqueror(app_name))
    return konq_instances

def get_konqueror_instance(name):

    "Return the Konqueror instance with the given DCOP identifying 'name'."

    client = get_client()
    return Konqueror(name)

# Classes representing the browser and the KHTML environment.

class Konqueror:

    "A class representing Konqueror browsers accessible via DCOP."

    def __init__(self, app_name):
        self.app_name = app_name

    def get_parts(self):
        client = get_client()
        obj_names = map(str, client.remoteObjects(self.app_name)[0])
        auto_roots = []
        for obj_name in obj_names:
            if obj_name.startswith("AutomationRoot"):
                auto_roots.append(AutomationRoot(self.app_name, obj_name))
        return auto_roots

class AutomationRoot:

    "A class representing the automation interface to a KHTML part."

    def __init__(self, app_name, obj_name):
        self.app_name = app_name
        self.obj_name = obj_name

    def get_remote_object(self):
        client = get_client()
        return dcopext.DCOPObj(self.app_name, client, self.obj_name)

    # Exported methods.

    def getURL(self):
        status, url = self.get_remote_object().getURL()
        return str(url)

    def openURL(self, url):
        self.get_remote_object().openURL(url)

    def closeURL(self):
        self.get_remote_object().closeURL()

    def baseURL(self):
        status, url = self.get_remote_object().baseURL()
        return str(url)

    def isReady(self):
        status, ready = self.get_remote_object().isReady()
        return ready

    def getDocument(self):
        remote_object = self.get_remote_object()
        status, result = remote_object.getDocument()
        if not status:
            raise RuntimeError, "No remote document found."

        try:
            return RemoteNode(result[1], remote_object)
        except IndexError:
            raise RuntimeError, "No remote document found."

# vim: tabstop=4 expandtab shiftwidth=4
