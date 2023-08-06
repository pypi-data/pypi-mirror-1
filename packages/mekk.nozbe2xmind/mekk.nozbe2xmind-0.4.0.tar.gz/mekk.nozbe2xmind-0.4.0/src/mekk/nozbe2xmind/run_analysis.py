# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.nozbe2xmind.xmind_reader import MapReader
from twisted.internet import defer

"""
Wysokiego poziomu funkcje do info/uploadu
"""
def print_changes_info(map_file_name):
    """
    Wypisanie informacji, co się zmieniło
    """
    project_deletes = []
    action_deletes = []
    
    reader = MapReader(map_file_name)
    print "*" * 60
    print "* The following changes will be saved to Nozbe"
    print "* if you run the upload command." 
    print "*" * 60
    print
    
    print "* Project changes"
    print
    for orig, new in reader.check_projects():
        if not new:
            project_deletes.append(orig)
        elif not orig:
            print "  (create) %(name)s" % new
            #print "      set:", ", ".join(new.iterkeys())
        else:
            if 'name' in new:
                print "  (modify) %s ==> %s" % (orig['name'], new['name'])
            else:
                print "  (modify) %(name)s" % orig
        if new:
            change_items = []
            for key, value in new.iteritems():
                if key == "id":
                    pass
                elif key == "name":
                    change_items.append("name edited")
                elif key == "date":
                    change_items.append("completion-flag edited")
                elif key == "body":
                    if value:
                        change_items.append("description edited")
                    elif orig:
                        change_items.append("description deleted")
                elif key == "tag":
                    if value:
                        change_items.append("tags edited")
                    elif orig:
                        change_items.append("tags deleted")
                else:
                    change_items.append("%s edited" % key)
            print "      changes:", ", ".join(change_items)
    print

    print "* Action changes"
    print
    for orig, new in reader.check_actions():
        if not new:
            action_deletes.append(orig)
        elif not orig:
            print "  (create) %(name)s" % new
        else:
            if 'name' in new:
                print "  (modify) %s ==> %s" % (orig['name'], new['name'])
            else:
                print "  (modify) %(name)s" % orig
        if new:
            change_items = []
            for key, value in new.iteritems():
                if key == "id":
                    pass
                elif key == "name":
                    change_items.append("name edited")
                elif key == "next":
                    if value:
                        change_items.append("set as next")
                    elif orig:
                        change_items.append("no longer next")
                elif key == "context_hash":
                    if value:
                        change_items.append("context changed")
                    elif orig:
                        change_items.append("context deleted")
                elif key == "project_hash" or key == "project_id":
                    if value:
                        change_items.append("project changed")
                    #elif orig:
                    #    change_items.append("tags deleted")
                elif key == "date":
                    if value:
                        change_items.append("marked complete")
                    elif orig:
                        change_items.append("cleared completion mark")
                else:
                    change_items.append("%s edited" % key)
            print "      changes:", ", ".join(change_items)

    print

    if project_deletes or action_deletes:
        print "*" * 60
        print "* The following changes will NOT be saved to Nozbe"
        print "* Consider making them manually." 
        print "*" * 60
        print
        for p in project_deletes:
            print "  (delete project) %(name)s" % p
        for p in action_deletes:
            print "  (delete action) %(name)s" % p

@defer.inlineCallbacks    
def upload_changes(nozbe_api, map_file_name):
    """
    Przeprowadzenie uploadu
    """

    project_deletes = []
    action_deletes = []
    
    reader = MapReader(map_file_name)

    print "*" * 60
    print "* Uploading project changes." 
    print "*" * 60
    print

    print "...calculating"

    count = 0
    prj_reqid_to_name = {}  # DO grepowania w czym błąd, mapa id requestu na nazwę
    prj_project_id_to_reqid = {} # Do wyszukiwania haszy projektów dla akcji w nowych
                                 # projektach. Mapuje id żądania na correlation id projektu
                                 # (które tu i w akcjach wpada jako 'project_id')
    for orig, new in reader.check_projects():
        if not new:
            project_deletes.append(orig)
        elif not orig:
            count += 1
            print "  (create) %(name)s" % new
            id = nozbe_api.add_project(new['name'], new['body'], new['tag'])
            prj_reqid_to_name[id] = new['name']
            prj_project_id_to_reqid[ new['project_id'] ] = id
        else:
            count += 1
            if 'name' in new:
                print "  (modify) %s ==> %s" % (orig['name'], new['name'])
            else:
                print "  (modify) %(name)s" % orig
            record = orig.copy()
            record.update(new)
            id = nozbe_api.update_project(record)
            prj_reqid_to_name[id] = orig['name']

    prj_reqid_to_hash = dict()
    if count:
        print
        print "...saving"
        reply = yield nozbe_api.save_changes()
        data = reply['project']
        for item in data.values(): # to jest o dziwo słownik id -> dane projektu
            id = item.get('id', '')
            name = prj_reqid_to_name.get(id, '?')
            if item.get('flag', '') == 'error':
                print "   Failed: %s, message: %s, field: %s" % (
                        name, item.get('message', ''), item.get('field', '-'))
            else:
                print "   Saved correctly: %s" % item.get('name')
                if id:
                    prj_reqid_to_hash[id] = item['hash']
    else:
        print "   no changes found"
    
    print

    #######################################################

    print "*" * 60
    print "* Uploading action changes." 
    print "*" * 60
    print

    print "...calculating"

    count = 0
    act_id2name = {} # Do grepowania w czym błąd
    for orig, new in reader.check_actions():
        if not new:
            action_deletes.append(orig)
            continue
        
        prid = new.get('project_id')
        if prid:
            reqid = prj_project_id_to_reqid[prid]
            new['project_hash'] = prj_reqid_to_hash.get(reqid)
            if not new['project_hash']:
                name = new.get('name') or orig.get('name')
                print "(skipping) Action %s not saved as it belongs to the project which failed to create" % name
                continue
        count += 1
        
        if not orig:
            id = nozbe_api.add_task(new['name'], new['project_hash'], 
                               context_hash = new.get('context_hash'),
                               next = new.get('next', 0),
                               date = new.get('date', 0))
            act_id2name[id] = new['name']

            print "  (create) %(name)s" % new
        else:
            record = orig.copy()
            record.update(new)
            id = nozbe_api.update_task(record)
            act_id2name[id] = record['name']
            
            if 'name' in new:
                print "  (modify) %s ==> %s" % (orig['name'], new['name'])
            else:
                print "  (modify) %(name)s" % orig

    if count:
        print
        print "...saving"
        reply = yield nozbe_api.save_changes()
        data = reply['task']
        for item in data.values(): # to jest o dziwo słownik id -> dane projektu
            id = item.get('id', '')
            name = act_id2name.get(id, '?')
            if item.get('flag', '') == 'error':
                print "   Failed: %s, message: %s, field: %s" % (
                        name, item.get('message', ''), item.get('field', '-'))
            else:
                print "   Saved correctly: %s" % item.get('name')
                if id:
                    prj_reqid_to_hash[id] = item['hash']

    else:
        print "  no changes found"

    print

    #######################################################
    
    if project_deletes or action_deletes:
        print "*" * 60
        print "* The following changes were NOT saved to Nozbe"
        print "* Consider making them manually." 
        print "*" * 60
        print
        for p in project_deletes:
            print "  (delete project) %(name)s" % p
        for p in action_deletes:
            print "  (delete action) %(name)s" % p

    print
    print "Now remove your mind-map (or write a note on it so you don't"
    print "try to upload it anymore)." 

    defer.returnValue(None)
