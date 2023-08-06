#!/usr/bin/env python
# -*- coding: utf8 -*-

#import os
import sys
import optparse
import re
import logging

from xmlrpclib import Fault as XMLRPCException

from lxml import etree
from wsapi4plone.client import getClient

parser = optparse.OptionParser()
parser.add_option("-u", "--url", help="The URL to the Plone site.", default="http://admin:admin@127.0.0.1:8080/plone", dest="url")
parser.add_option("-f", "--file", help="The file name to the MS Project XML file", default="project.xml", dest="filename")
parser.add_option("-p", "--path", help="The root path to the container to create the XM project in.", default="/plone", dest="path")
parser.add_option("-m", "--mode", help="Either 'merlin' or 'ms project'", dest="mode", default="ms project")
parser.add_option("-v", "--verbose", help="Be more verbose.", dest="verbose", action="store_true", default=False)
parser.add_option("-q", "--quiet", help="Be quiet.", dest="verbose", action="store_false", default=False)
parser.add_option("-d", "--debug", help="Print debugging messages.", dest="debug", action="store_true", default=False)

def parse_duration(duration):
    """
    parse duration format: PT31H59M59S#{{{

    >>> parse_duration("PT10H0M0S")
    (10, 0, 0)
    >>> parse_duration("PT0H4M30S")
    (0, 4, 30)
    >>> parse_duration("foo") is None
    True

    """
    m = re.match(r"PT(\d+)H(\d+)M(\d+)S", duration)
    if m:
        return tuple(map( int, m.groups()))#}}}

def create_object(client, path, title, description, type_name, update=True, **kw):#{{{
    """
    ploneid;ID;Titel;Beschreibung;Postal Code;City;Street
    """
    schema = {
            'title':            title.encode("utf8"),
            'description':      description.encode("utf8"),
    }

    schema.update(kw)

    for k, v in schema.items():
        if not v:
            del schema[k]

    obj = { path: [schema, type_name]}

    o = None
    try:
        o = client.get_object([path])
        if not update:
            return o
    except XMLRPCException:
        pass
    if o:
        logging.info( "UPDATE: %10s %20s %s" % (type_name, path, title))
        return client.get_object(client.put_object(obj))
        # return client.get_object(client.put_object(obj))
    else:
        logging.info( "CREATE: %10s %20s %s" % (type_name, path, title))
        return client.post_object(obj)
        # return client.get_object(client.post_object(obj))#}}}

def create_project(client, path, title, description, budget_hours=0, billable=True,
        include_global_employees=True):
    """#{{{
        {'/plone/foo': [{'allowDiscussion': False,
                         'billableProject': True,
                         'budgetHours': None,
                         'contributors': [],
                         'creation_date': <DateTime '2010-01-28T12:15:49+01:00' at 1032aa8>,
                         'creators': ['admin'],
                         'description': '123 123',
                         'effectiveDate': None,
                         'expirationDate': None,
                         'id': 'foo',
                         'includeGlobalMembers': True,
                         'language': '',
                         'location': '',
                         'modification_date': <DateTime '2010-01-28T12:15:49+01:00' at 1089030>,
                         'rights': '',
                         'subject': [],
                         'title': 'foo'},
                        'Project',
                        {}]}
    """
    type_name = "Project"
    o = create_object(client, path, title, description, type_name=type_name,
            billableProject=billable, budgetHours=budget_hours, includeGlobalMembers=include_global_employees)
    return o#}}}

def create_iteration(client, path, title, description, man_hours=0, start_date=None, end_date=None):
    """#{{{

    {'/plone/foo/iter1': [{'allowDiscussion': False,
                           'contributors': [],
                           'creation_date': <DateTime '2010-01-28T12:22:42+01:00' at 1089440>,
                           'creators': ['admin'],
                           'description': '123 123',
                           'effectiveDate': None,
                           'endDate': None,
                           'expirationDate': None,
                           'id': 'iter1',
                           'language': '',
                           'location': '',
                           'manHours': None,
                           'modification_date': <DateTime '2010-01-28T12:22:42+01:00' at 10894b8>,
                           'rights': '',
                           'startDate': <DateTime '2010-01-28T12:22:42+01:00' at 10893a0>,
                           'subject': [],
                           'title': 'bar'},
                          'Iteration',
                          {}]}

    """
    type_name = "Iteration"
    o = create_object(client, path, title, description, type_name=type_name, manHours=man_hours, startDate=start_date,
            endDate=end_date)
    return o#}}}

def create_story(client, path, title, description, text='', estimate_days=0):#{{{
    """
    {'/plone/foo/iter1/story1': [{'allowDiscussion': False,
                                  'contributors': [],
                                  'creation_date': <DateTime '2010-01-28T12:30:03+01:00' at 10891e8>,
                                  'creators': ['admin'],
                                  'description': '123 123',
                                  'effectiveDate': None,
                                  'expirationDate': None,
                                  'id': 'story1',
                                  'language': '',
                                  'location': '',
                                  'mainText': '',
                                  'modification_date': <DateTime '2010-01-28T12:30:03+01:00' at 1089350>,
                                  'rights': '',
                                  'roughEstimate': None,
                                  'subject': [],
                                  'title': 'bar'},
                                 'Story',
                                 {}]}
    """
    o = create_object(client, path, title, description, type_name="Story",
            roughEstimate=estimate_days, mainText=text)

    # move story to "estimated" if we have a estimate
    if estimate_days:
        state = client.get_workflow(path)
        if state["state"] == "draft":
            client.set_workflow("estimate", path)

    if text:
        text_new = []
        task_id = 0
        for line in text.splitlines():
            if line.startswith("task:"):
                task_desc = line[len("task:"):]
                task_id += 1
                create_task(client, "%s/task_%s" % (path, task_id), task_desc)
            else:
                text_new.append(line)

        # update text
        o = create_object(client, path, title, description, type_name="Story",
                roughEstimate=estimate_days, mainText="\n".join(text_new))
    return o
    #}}}

def create_task(client, path, task_desc):
    """
    Create a task#{{{

    {'/plone/foo/iter1/story1/task1': [{'allowDiscussion': False,
                                        'assignees': [],
                                        'contributors': [],
                                        'creation_date': <DateTime '2010-01-28T13:26:10+01:00' at 108eaa8>,
                                        'creators': ['admin'],
                                        'description': '123 123',
                                        'effectiveDate': None,
                                        'expirationDate': None,
                                        'hours': 0,
                                        'id': 'task1',
                                        'language': '',
                                        'location': '',
                                        'mainText': '',
                                        'minutes': 0,
                                        'modification_date': <DateTime '2010-01-28T13:26:10+01:00' at 108eb20>,
                                        'rights': '',
                                        'subject': [],
                                        'title': 'bar'},
                                       'Task',
                                       {}]}
    
    task_desc::

        http://docs.google.com/Doc?docid=0AYm9YUhGM9slZGN2Ym50azhfMmM2eHZjZmR6&hl=en

        title # hours # employee

    """
    hours = 0
    assignees = []
    try:
        title, hours, assignees = map(lambda x: x.strip(), task_desc.split("#"))
        hours = int(hours)
        assignees = assignees.split(",")
    except:
        title = task_desc

    o = create_object(client, path, title, description="", type_name="Task",
            hours=hours, minutes=0, assignees=assignees)
    return o#}}}

class MSPImport(object):
    """

    Parse a file::

        >>> f = file("SETTR Installation.xml")
        >>> p = MSPImport(f)
        >>> p.tree
        <lxml.etree._ElementTree object at ...>

    Fetch all the tasks::

        >>> len(p.tasks())
        41

    Tasks are Elements::

       >>> p.tasks()[0].tag == "Task"
       True

    """

    MODE_MERLIN = 0
    MODE_MSPROJECT = 1

    OUTLINE_PROJECT = 0
    OUTLINE_ITERATION = 1
    OUTLINE_STORY = 2

    NS = "http://schemas.microsoft.com/project"

    NSMAP = { None: NS }

    def __init__(self, f, mode=MODE_MSPROJECT):
        logging.info("parsing file: %s" % f)
        self.tree = etree.parse(f)
        self.mode = mode
        logging.info("Switching to mode %d" % self.mode)

    def find(self, e, path):
        return e.find( "{%s}%s" % (self.NS, path))

    def findall(self, e, path):
        return e.findall( "{%s}%s" % (self.NS, path))


    def tasks(self):
        tasks = self.find(self.tree, "Tasks")
        if tasks is None:
            raise RuntimeError("Can't find 'Tasks' Node -- is this a MS Project XML?")

        return self.findall(tasks, "Task")

    def get_node_val(self, task, tag):
        n = self.find(task, tag)
        if n is not None:
            logging.debug("task %s: %s -> %s" % (task, tag, n.text))
            return n.text
        logging.debug("task %s: %s NONE" % (task, tag))
        return ""

    def get_level(self, task):
        return int(self.get_node_val(task, "OutlineLevel"))

    def get_uid(self, task):
        return self.get_node_val(task, "UID")

    def get_name(self, task):
        return self.get_node_val(task, "Name")

    def is_milestone(self, task):
        return int(self.get_node_val(task, "Milestone"))

    def get_duration(self, task):
        d = self.get_node_val(task, "Duration")
        d = parse_duration(d)
        if d:
            return d[0]
        return 0

    def get_work(self, task):
        d = self.get_node_val(task, "Work")
        d = parse_duration(d)
        if d:
            return d[0]
        return 0


    def get_note(self, task):
        return self.get_node_val(task, "Notes")

    def get_date(self, task, tag):
        date = self.get_node_val(task, tag)
        return date

    def _import(self, client, root_path):
        project = None
        iteration = None
        for t in self.tasks():
            logging.info("Task: %s" % t)

            level = self.get_level(t)
            description = title = self.get_name(t)
            uid = self.get_uid(t)

            # XXX: MS Project allows for multiple projects per project plan.
            if self.mode == self.MODE_MSPROJECT:
                level -=1

            if self.is_milestone(t):
                print >>sys.stderr, "Ignoring milestone:", description
                continue

            if level == self.OUTLINE_PROJECT:#{{{
                # Projekt anlegen
                path = "/".join([root_path, uid])

                # XXX: Work oder Duration???
                hours = self.get_duration(t)

                # XXX: only hours??
                create_project(client, path, title, description, budget_hours=hours)


                project = path
                iteration = None#}}}

            elif level == self.OUTLINE_ITERATION:#{{{
                # Iteration
                if not project:
                    raise RuntimeError("Parse error: Iteration w/o Project.")

                hours = self.get_duration(t)

                start_date = self.get_date(t, "Start")
                end_date = self.get_date(t, "Finish")

                path = "/".join([project, uid])
                create_iteration(client, path, title, description, man_hours=hours, start_date=start_date,
                        end_date=end_date)

                iteration = path#}}}

            elif level == self.OUTLINE_STORY:#{{{
                # Story
                if not iteration:
                    raise RuntimeError("Parse error: Strory w/o Iteration.")

                hours = self.get_duration(t)
                text = self.get_note(t)

                days = (hours / 8)
                if hours % 8:
                    days += 1

                path = "/".join([iteration, uid])
                create_story(client, path, title, description, text, days)#}}}


def msp2plone():
    options, args = parser.parse_args()

    if options.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not options.url:
        print >>sys.stderr, "Need a URL."
        sys.exit(10)

    if not options.filename:
        print >>sys.stderr, "Need a File Name."
        sys.exit(10)

    if options.mode == "merlin":
        mode = MSPImport.MODE_MERLIN
    elif options.mode == "ms project":
        mode = MSPImport.MODE_MSPROJECT
    else:
        raise RuntimeError("Unknown mode: %s" % options.mode)

    imp = MSPImport(options.filename, mode=mode)
    client = getClient(options.url)
    imp._import(client, options.path)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
