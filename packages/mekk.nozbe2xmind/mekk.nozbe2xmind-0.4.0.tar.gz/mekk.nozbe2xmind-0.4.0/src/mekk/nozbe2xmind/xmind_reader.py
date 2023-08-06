# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.xmind import XMindDocument
from xmind_writer import NEXT_ACTION_MARK, DONE_MARK
from context_icons import IconsMapper
import simplejson
import logging
import datetime
import re

log = logging.getLogger(__name__)

def find_mismatches(old, new, checked_tags):
    """
    Znajduje wszystkie tagi dla których old[tag] != new[tag]
    i zwraca je w formie słownika
    """
    reply = {}
    for t in checked_tags:
        o = old.get(t)
        if o is None: o = ''
        n = new.get(t)
        if n is None: n = ''
        if o != n:
            #log.debug("Changed %s: '%s' -> '%s'" % (t, old.get(t), new.get(t)))
            reply[t] = n
    return reply

class MapReader(object):
    """
    Klasa obsługująca odczyt zmodyfikowanej mapy i zwracająca informacje, co się na tej mapie zmieniło.
    """

    def __init__(self, map_file_name):
        self.file_name = map_file_name
        self.doc = XMindDocument.open(map_file_name)
        self._load_orig_data()
        self.root = self.doc.get_first_sheet().get_root_topic()

    def _load_orig_data(self):
        """
        Wyszukuje w mapie załączony plik JSON i ładuje z niego dane (oryginały do porównania)
        """
        jsons = [j for j in self.doc.attachment_names() if j.endswith('.json') ]
        if not jsons:
            raise Exception("Map can not be processed, attached data file not found. Likely you removed the attachment from the help sheet")
        if len(jsons) > 1:
            raise Exception("Map can not be processed, too many data files attached.")
        data = simplejson.loads(self.doc.attachment_body(jsons[0]))
        self.orig_actions = data['actions']
        self.orig_projects = data['projects']
        self.orig_contexts = data['contexts']

    def check_projects(self):
        """
        Wyszukanie zmian w projektach. Generator, który zwraca listę zmienionych projektów.
        Każda zmiana ma formę pary orig, new, gdzie:

        - orig jest poprzednim, nie zmienionym rekordem projektu
          albo None, gdy zmianą jest dodanie nowego projektu

        - new jest słownikiem zmian (zmienione pola wraz z wartościami)
          albo None, gdy zmianą jest usunięcie projektu.

        Uwaga: prosty sposób na uzyskanie rekordu "do zapisu" przy
        modyfikacjach to:

           orig.copy().update(new)

        Nowe projekty (i tylko one) zawierają pole id umożliwiające
        korelację z akcjami.
        """
        orig_lkp = dict([ (p['hash'], p) for p in self.orig_projects ])

        for project_topic in self.root.get_subtopics():
            new = dict(
                       name = project_topic.get_title(),
                       tag = project_topic.get_label() or '',
                       body = project_topic.get_note() or '',
                       )
            hash = project_topic.get_embedded_id()
            if not hash:
                # Nowy projekt, nieoznakowany
                new['project_id'] = project_topic.get_correlation_id()
                yield None, new
            else:
                old = orig_lkp[ hash ]
                del orig_lkp[hash]  # By zostały tylko skasowane
                mism = find_mismatches(old, new, ['name', 'tag', 'body'])
                if mism:
                    log.debug("Changed field(s) in %s: %s" % (hash, mism))
                    yield old, mism
        # Zostały skasowane
        for old in orig_lkp.itervalues():
            yield old, None

    def check_actions(self):
        """
        Wyszukanie zmian w akcjach. Generator obsługujący tą samą
        konwencję, co check_projects, tj zwraca pary orginał-zmiany,
        gdzie stare jest None gdy coś dodano a nowe jest None gdy
        coś skasowano a wpp zawiera zmienione pola.

        Uwaga: akcje mogą zawierać albo project_hash (akcja jest
        w "starym" projekcie) albo project_id (akcja jest podpięta
        do nowo dodanego projektu, koreluje się to z polem id
        zwróconym przez check_projects). Przed zapisem trzeba
        project_id zamienić na project_hash.

        Ponadto nowe akcje zawierają pewne unikalne id.
        """
        orig_lkp = dict([ (p['hash'], p) for p in self.orig_actions ])

        ctx_name_to_obj = dict(
            (ctx['name'], ctx) for ctx in self.orig_contexts)

        # Lista nowych akcji. Nie zwracamy od razu, bo chcemy zrobić
        # dopasowanie z skasowanymi (wykrywanie cut&paste)
        added = []

        for project_topic in self.root.get_subtopics():
            project_hash = project_topic.get_embedded_id()
            if not project_hash:
                project_id = project_topic.get_correlation_id()

            # Tablica jeszcze nie obsłużonych akcji. Trzymamy
            # tak, bo trzeba włazić rekurencyjnie w głąb

            now_time = datetime.datetime.now().strftime("%Y-%m-%d %T")

            pending = list( project_topic.get_subtopics() )
            while pending:
                action_topic = pending.pop(0)
                hash = action_topic.get_embedded_id()

                subactions = list( action_topic.get_subtopics() )
                if subactions:
                    pending.extend(subactions)
                    # Jeśli to jest nowe a miało dzieci, uznajemy
                    # za blog pomocniczy
                    if not hash:
                        continue

                markers = list( action_topic.get_markers() )

                new = {
                       u"name" : action_topic.get_title(),
                       u"next" : (NEXT_ACTION_MARK in markers) and 1 or 0,
                       u"context_hash" : '',
                       }
                if project_hash:
                    new["project_hash"] = project_hash
                else:
                    new["project_id"] = project_id
                if DONE_MARK in markers:
                    # Chwilowy znacznik
                    new["done"] = True
                else:
                    new["done"] = False

                action_labels = [ l 
                                  for l in re.split("\s*,\s*",
                                                    action_topic.get_label() or "")
                                  if l ]
                for ctx_name in action_labels:
                    ctx = ctx_name_to_obj.get(ctx_name)
                    if ctx:
                        new["context_hash"] = ctx['hash']
                    else:
                        print "Unknown context, skipping:", ctx_name

                if not hash:
                    # Nowa akcja
                    new['id'] = action_topic.get_correlation_id()
                    if new['done']:
                        new['date'] = now_time
                    del new['done']
                    #yield None, new
                    added.append(new)
                else:
                    old = orig_lkp[ hash ]
                    del orig_lkp[hash]  # By zostały tylko skasowane
                    # Nie przestawiamy daty zakończenia jeśli zachowała się
                    #if new.get('datetime') and old.get('datetime'):
                    #    new['datetime'] = old['datetime']
                    mism = find_mismatches(old, new, [
                        'name', 'next', 'project_hash', 'context_hash'])
                    # Specjalne flagowanie przepisania do nowego projektu
                    if new.get('project_id'):
                        mism['project_id'] = new['project_id']
                    # Specjalna obsługa 'date' (czy zrobione + kiedy) versus 'done':
                    if old.get('date', '') and not new['done']:
                        mism['date'] = ''   # Zdjęto znacznik done
                    elif (not old.get('date', '')) and new['done']:
                        mism['date'] = now_time  # Założono go
                    if mism:
                        log.debug("Changed field(s) in %s: %s" % (hash, mism))
                        yield old, mism

        for a in added:
            yield None, a
        # Zostały skasowane
        for old in orig_lkp.itervalues():
            yield old, None

