# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

"""
Obsługa translacji między nazwami a identyfikatorami ikonek
"""

from pkg_resources import resource_stream, resource_filename
import zipfile
from lxml import etree

ICONS = "NozbeIconsMarkerPackage.xmp"
SHEET = "markerSheet.xml"

class IconsMapper(object):
    def __init__(self):
        zf = zipfile.ZipFile(resource_stream(__name__, ICONS), "r")
        xt = zf.read(SHEET)
        et = etree.XML(xt)
        #print etree.tostring(et, pretty_print=True)
        icon2id = dict()
        id2icon = dict()
        for marker in et.iter("{urn:xmind:xmap:xmlns:marker:2.0}marker"):
            id = marker.get("id")
            name = marker.get("name")
            icon2id[name] = id
            id2icon[id] = name
            #print " %s: %s" % (marker.get("id"), marker.get("name"))
        self._icon2id = icon2id
        self._id2icon = id2icon
    def id_for_icon(self, icon):
        return self._icon2id.get(icon, None)
    def icon_for_id(self, id):
        return self._id2icon.get(id, None)
    def xmp_filename(self):
        return resource_filename(__name__, ICONS)

if __name__ == "__main__":
    m = IconsMapper()
    print m.id_for_icon("icon-51.png")
    print m.icon_for_id("3hrj4o7ed3gcloi2me53at5g79")
