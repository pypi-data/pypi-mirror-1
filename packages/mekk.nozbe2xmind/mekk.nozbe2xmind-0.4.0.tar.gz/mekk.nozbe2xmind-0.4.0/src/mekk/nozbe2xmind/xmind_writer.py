# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.xmind import XMindDocument, XMIND_MARKS
from mekk.nozbe import NozbeApi
import simplejson
from twisted.internet import defer
import context_icons

# Znaczniki używane do kontekstów
NEXT_ACTION_MARK = 'task-start'
DONE_MARK = 'task-done'
SHARED_MARK = 'other-people'
RECUR_MARK = 'task-quarter'

# URLe
PRODUCTION_PROJECT_URL = "http://www.nozbe.com/account/projects/show-%s"
DEVEL_PROJECT_URL = "http://devl.nozbe.net/account/projects/show-%s"

class MarkerGen(object):
    """
    Klasa przypisująca ikonom kontekstów z Nozbe markery dla XMinda
    """
    def __init__(self):
        self.ci = context_icons.IconsMapper()
    def xmp_filename(self):
        return self.ci.xmp_filename()
    def give_mark(self, icon):
        if icon is None or icon == "icon-.png":
            return None
        return self.ci.id_for_icon(icon)

@defer.inlineCallbacks
def nozbe_to_xmind(nozbe_client, xmind_filename, devel = False, include_completed = False):
    """
    Podłącza się do zadanego konta XMind, pobiera projekty,
    konteksty i akcje i wszystko zapisuje

    @param nozbe_client: obiekt ładujący (zwykle NozbeApi(api_key) ale można do testów inne)
    @param xmind_filename: tworzony plik .xmind
    @param devel: ustawiane gdy używamy sajtu developerskiego
    @param include_completed: czy ściągać także zakończone akcje
    """
    assert(isinstance(nozbe_client, NozbeApi))

    #all_actions = []

    if not devel:
        project_url = PRODUCTION_PROJECT_URL
    else:
        project_url = DEVEL_PROJECT_URL

    xmw = XMindDocument.create("Projects", "Projects")
    sheet = xmw.get_first_sheet()
    project_root = sheet.get_root_topic()
    project_root.set_note("View the Help sheet\n(click Help tab in the bottom left corner)\nfor info what you can do\nwith this map")

    marker_gen = MarkerGen()
    xmw.embed_markers(marker_gen.xmp_filename())

    print "Loading projects (it may take a minute or two)..."
    projects = yield nozbe_client.get_projects()
    if projects is None:
        projects = []
    print "   DONE."

    print "Loading contexts"
    contexts = yield nozbe_client.get_contexts()
    print "   DONE."

    #context_hash_to_icon = dict( [ (c['hash'], "icon-%s.png" % c['icon']) for c in contexts ] ) 
    context_hash_to_obj = dict( (c['hash'], c) for c in contexts )

    print "Loading actions (it may take a few minutes if you have many)..."
    all_actions = yield nozbe_client.get_tasks()
    if all_actions is None:
        all_actions = []
    print "   DONE."
    
    if include_completed:
        print "Loading finished actions..."
        finished_actions = yield nozbe_client.get_completed_tasks()
        if finished_actions:
            all_actions.extend(finished_actions)
        print "   DONE."

    project_topics = dict()       # id projektu -> Topic

    project_style = xmw.create_topic_style(fill = "#37D02B")

    for p in projects:
        p_hash = p['hash']
        p_topic = project_root.add_subtopic(p['name'], p_hash)
        p_id = p.get('id', None)
        if p_id:
            p_topic.set_link(project_url % p_id)
        p_topic.set_style(project_style)
        p_tag = p['tag']
        if p_tag:
            p_topic.set_label(p_tag)
        p_body = p['body']
        if p_body:
            p_topic.set_note(p_body)
        if p.get('share'):
            p_topic.add_marker(SHARED_MARK)

        actions = [act for act in all_actions if act['project_hash'] == p_hash]

        for action in actions:
            # Każda akcja ma 'id', 'name', 'name_show', 'done', 'time', 'project_id',
            # 'project_name', 'context_id', 'context_name', 'context_icon', 'next'
            a_topic = p_topic.add_subtopic(action['name'], action['hash'])
            if action['next']:
                a_topic.add_marker(NEXT_ACTION_MARK)
            if action['date']:   # w starym api było 'done'...
                a_topic.add_marker(DONE_MARK)
            if action['recur'] and action['recur'] != "0":
                a_topic.add_marker(RECUR_MARK)
            c_hash = action['context_hash']
            if c_hash:
                a_topic.set_label(context_hash_to_obj[c_hash]['name'])
                #c_mark = marker_gen.give_mark(context_hash_to_icon.get(c_hash, None))
                #if c_mark:
                #    a_topic.add_marker(c_mark)

    # Legenda.
    legend = sheet.get_legend()
    legend.add_marker(NEXT_ACTION_MARK, "Next action")
    legend.add_marker(DONE_MARK, "Done")
    legend.add_marker(SHARED_MARK, "Shared")
    legend.add_marker(RECUR_MARK, "Recurring")
    # Not adding context icons anymore, they aren't in fashion 
    #if contexts:
    #    for c in contexts:
    #        c_mark = marker_gen.give_mark("icon-%s.png" % c["icon"])
    #        if c_mark:
    #            legend.add_marker(c_mark, c["name"])

    # Legenda po raz drugi (potrzebne by xmind użył wszystkich ikonek)
    if p_topic:
        topic_legend = p_topic.add_subtopic("MarkersList", detached=True)
    else:
        topic_legend = project_root.add_subtopic("MarkersList", detached=True)
    topic_legend.add_subtopic("Needed to make sure XMind knows all markers")
    topic_legend.add_subtopic("Feel free to move this anywhere or delete")
    topic_legend.add_subtopic("Next action").add_marker(NEXT_ACTION_MARK)
    topic_legend.add_subtopic("Done").add_marker(DONE_MARK)
    topic_legend.add_subtopic("Shared").add_marker(SHARED_MARK)
    topic_legend.add_subtopic("Recurring").add_marker(RECUR_MARK)
    #if contexts:
    #    for c in contexts:
    #        c_mark = marker_gen.give_mark("icon-%s.png" % c["icon"])
    #        if c_mark:
    #            topic_legend.add_subtopic(c["name"]).add_marker(c_mark)

    info_sheet = xmw.create_sheet("Help", "What you can do\nwith this map")
    info_root = info_sheet.get_root_topic()
    info_root.set_note("""Do not remove the attachment! It is necessary to save your changes back.""")
    info_root.set_attachment(
        simplejson.dumps(dict(projects = projects, contexts = contexts, actions = all_actions)),
        ".json")
    e = info_root.add_subtopic("Everything")
    e.add_subtopic("But keep the rules below if you want to save back to Nozbe")
    e.add_subtopic("The saving script ignores everything it does not understand").add_subtopic("Including deletes")
    proj = info_root.add_subtopic("Edit Projects")
    proj.add_subtopic("Rename")
    d = proj.add_subtopic("Edit description")
    d.add_subtopic("As Notes (F4)")
    d.add_subtopic("only plain text please")
    et = proj.add_subtopic("Edit tags")
    et.add_subtopic("As Label (F3)")
    et.add_subtopic("Space separated")
    proj.add_subtopic("Create").add_subtopic("As direct child of the map root")
    act = info_root.add_subtopic("Edit Actions")
    act.add_subtopic("Rename")
    act.add_subtopic("Move between projects")
    act.add_subtopic("Create").add_subtopic("Under new or existing projects")
    act.add_subtopic("Flag as completed").add_marker(DONE_MARK)
    fn = act.add_subtopic("Flag as next")
    fn.add_marker(NEXT_ACTION_MARK)
    fn.add_subtopic("Or clear this flag")
    ec = fn.add_subtopic("Edit context")
    ec.add_subtopic("As Label (F3)")
    ec.add_subtopic("Name must match existing context")
    ec.add_subtopic("Multiple contexts not yet handled").add_subtopic("In the future they will be ,-separated")
    
    extra = info_root.add_subtopic("Extra conventions")
    t = extra.add_subtopic("Use intermediate nodes")
    t.add_subtopic("Between projects and actions").add_subtopic("Also multilevel")
    t.add_subtopic("Any leaf is an action")
    t.add_subtopic("Intermediate nodes are ignored")

    cng = info_root.add_subtopic("Check what you changed")
    cng.add_subtopic("Save map")
    cng.add_subtopic("Run xmind2nozbe info file.xmind")
    ing = info_root.add_subtopic("Save changes back to Nozbe")
    ing.add_subtopic("Save map")
    ing.add_subtopic("Run xmind2nozbe upload file.xmind")
    ing.add_subtopic("Do it only once").add_subtopic("Or you can add the same action twice")

    xmw.save(xmind_filename)

