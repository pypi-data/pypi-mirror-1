#!/usr/bin/env python

import qtxmldom, qtxmldom.remote
from kdecore import KApplication
import sys

def choose(objects, attr, prompt):
    if len(objects) == 1:
        return objects[0]
    elif len(objects) > 1:
        names = {}
        for obj in objects:
            names[str(getattr(obj, attr))] = obj
        print ", ".join(names.keys())
        name = raw_input(prompt)
        return names[name]
    else:
        print "Please start a Konqueror instance and open a Web page."
        sys.exit(1)

app = KApplication(["Test"], "Test")
apps = qtxmldom.remote.get_konqueror_instances()
konq = choose(apps, "app_name", "Which application? ")
parts = konq.get_parts()
part = choose(parts, "obj_name", "Which part? ")
obj = part.get_remote_object()
doc = qtxmldom.fromRemoteObject(obj)
print doc.toString()

# vim: tabstop=4 expandtab shiftwidth=4
