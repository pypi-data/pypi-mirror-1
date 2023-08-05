#!/usr/bin/env python

from kdecore import KApplication
import dcopext

def get_client():
    app = KApplication.kApplication()
    if app is None:
        raise RuntimeError, "No KApplication initialised."
    return app.dcopClient()

def get_konqueror_instances():
    client = get_client()
    app_names = map(str, client.registeredApplications())
    konq_instances = []
    for app_name in app_names:
        if app_name.startswith("konqueror"):
            konq_instances.append(Konqueror(app_name))
    return konq_instances

class Konqueror:
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
    def __init__(self, app_name, obj_name):
        self.app_name = app_name
        self.obj_name = obj_name

    def get_remote_object(self):
        client = get_client()
        return dcopext.DCOPObj(self.app_name, client, self.obj_name)

# vim: tabstop=4 expandtab shiftwidth=4
