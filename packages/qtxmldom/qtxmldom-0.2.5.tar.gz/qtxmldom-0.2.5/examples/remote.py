#!/usr/bin/env python

"An example of remote document access."

import qtxmldom, qtxmldom.remote
from kdecore import KApplication
import sys
import time

# Browser opening support for added convenience.

try:
    import desktop
except ImportError:
    import webbrowser as desktop

# Functions which help find browsers and parts.

def choose(objects, attr, info_attr, prompt):
    if len(objects) == 1:
        return objects[0]
    elif len(objects) > 1:
        names = {}
        for obj in objects:
            names[str(getattr(obj, attr))] = obj
        for name, obj in names.items():
            if info_attr is not None:
                print name, "(" + getattr(obj, info_attr)() + ")"
            else:
                print name
        name = raw_input(prompt)
        return names[name]
    else:
        print "Please start a Konqueror instance and open a Web page."
        sys.exit(1)

def find_part(apps, url):
    if url is not None:
        for konq in apps:
            for p in konq.get_parts():
                if p.getURL() == url or p.getURL() == url + "/":
                    return p
    return None

# The main program which optionally opens a browser and then provides the remote
# document in the 'doc' variable.

if __name__ == "__main__":
    app = KApplication([sys.argv[0]], sys.argv[0])
    try:
        open_switch = sys.argv.index("--open")
        url = sys.argv[open_switch + 1]
        pid = desktop.open(url)
    except (ValueError, IndexError):
        url = None

    apps = qtxmldom.remote.get_konqueror_instances()
    part = find_part(apps, url)

    if part is None:
        konq = choose(apps, "app_name", None, "Which application? ")
        parts = konq.get_parts()
        part = choose(parts, "obj_name", "getURL", "Which part? ")

    # NOTE: Nasty hack to wait for the document to load.
    # NOTE: This is necessary because some Web sites perform redirects which
    # NOTE: change the state of the remote part, and we must wait for things to
    # NOTE: settle down.

    while not part.isReady():
        print "Waiting..."
        time.sleep(1)

    doc = qtxmldom.fromRemoteNode(part.getDocument())
    print doc.toString()

# vim: tabstop=4 expandtab shiftwidth=4
