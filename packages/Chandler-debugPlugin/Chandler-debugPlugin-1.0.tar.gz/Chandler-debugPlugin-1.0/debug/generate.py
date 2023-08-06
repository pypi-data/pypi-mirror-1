# -*- coding: utf-8 -*-

#   Copyright (c) 2003-2008 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Generate sample items: calendar, contacts, etc.
"""

import random

from datetime import datetime, timedelta
from osaf import pim
import osaf.pim.calendar.Calendar as Calendar
from osaf.pim import Modification
import osaf.pim.mail as Mail
import i18n
try:
    from i18n.tests import uw
except ImportError:
    uw = lambda _:_ # make uw a no-op
from application import schema

TEST_I18N = i18n.getLocaleSet() and 'test' in i18n.getLocaleSet()

HEADLINES = ["Dinner", "Lunch", "Meeting", "Movie", "Games"]

DURATIONS = [60, 90, 120, 150, 180]

REMINDERS = [None, None, None, None, 1, 10] # The "None"s make only a 30% chance an event will have a reminder...

def GenerateCalendarParticipant(view):
    domainName = random.choice(DOMAIN_LIST)
    handle = random.choice(LASTNAMES).lower()
    email = Mail.EmailAddress.getEmailAddress(view, 
                                              "%s@%s" % (handle, domainName))
    return email

LOCATIONS  = [u"Home", u"Office", u"School"]


def randomEnum(cls):
    return getattr(cls, cls.values.keys()[random.randint(0, len(cls.values)-1)])
    
def GenerateCalendarEvent(view, days=30, tzinfo=None):
    if tzinfo is None:
        tzinfo = view.tzinfo.floating
    event = Calendar.CalendarEvent(itsView=view)
    event.summary = random.choice(HEADLINES)

    if TEST_I18N:
        event.summary = uw(event.summary)

    # Choose random days, hours
    startDelta = timedelta(days=random.randint(0, days),
                           hours=random.randint(0, 24))

    now = datetime.now(tzinfo)
    closeToNow = datetime(now.year, now.month, now.day, now.hour,
                          int(now.minute/30) * 30, tzinfo=now.tzinfo)
    event.startTime = closeToNow + startDelta

    # Events are anyTime by default. Give a 5% chance of allDay instead,
    # or 90% of a normal event.
    r = random.randint(0,100)
    if r < 95: # 5% chance that we'll leave anyTime on
        event.anyTime = False
    if r < 5: # 5% chance of allDay
        event.allDay = True

    # Choose random minutes
    event.duration = timedelta(minutes=random.choice(DURATIONS))
    
    # Maybe a nice reminder?
    reminderInterval = random.choice(REMINDERS)
    if reminderInterval is not None:
        event.userReminderInterval = timedelta(minutes=-reminderInterval)
        
    # Add a location to 2/3 of the events
    if random.randrange(3) > 0:
        if TEST_I18N:
            event.location = Calendar.Location.getLocation(view, uw(random.choice(LOCATIONS)))
        else:
            event.location = Calendar.Location.getLocation(view, random.choice(LOCATIONS))

    event.itsItem.importance = random.choice(pim.ImportanceEnum.values)
    event.itsItem.setTriageStatus(randomEnum(pim.TriageEnum))
    return event.itsItem


TITLES = [u"reading list", u"restaurant recommendation", u"vacation ideas",
          u"grocery list", u"gift ideas", u"life goals", u"fantastic recipe",
          u"garden plans", u"funny joke", u"story idea", u"poem"]

EVENT, TASK, BOTH = range(2, 5)
M_TEXT  = u"This is a test email message"
M_EVENT = u" that has been stamped as a Calendar Event"
M_TASK  = u" that has been stamped as a Task"
M_BOTH  = u" that has been stamped as a Task and a Calendar Event"
M_FROM  = None

def GenerateMailMessage(view, tzinfo=None):
    global M_FROM
    message  = Mail.MailMessage(itsView=view)
    body     = M_TEXT

    outbound = random.randint(0, 1)
    type     = random.randint(1, 8)
    numTo    = random.randint(1, 3)

    if M_FROM is None:
        M_FROM = GenerateCalendarParticipant(view)

    message.fromAddress = M_FROM

    for num in range(numTo):
        message.toAddress.append(GenerateCalendarParticipant(view))

    message.subject  = random.choice(TITLES)

    if TEST_I18N:
        message.subject = uw(message.subject)

    message.dateSent = datetime.now(tzinfo)

    if outbound:
        message.outgoingMessage()
        message.itsItem.changeEditState(Modification.sent, who=M_FROM)

    else:
        message.incomingMessage()

    if type == EVENT:
        Calendar.EventStamp(message).add()
        body += M_EVENT

    if type == TASK:
        pim.TaskStamp(message).add()
        body += M_TASK

    if type == BOTH:
        Calendar.EventStamp(message).add()
        pim.TaskStamp(message).add()
        body += M_BOTH

    if TEST_I18N:
        body = uw(body)

    message.body = body
    message.itsItem.setTriageStatus(randomEnum(pim.TriageEnum))

    return message.itsItem

def GenerateNote(view, tzinfo=None):
    """ Generate one Note item """
    note = pim.Note(itsView=view)
    note.displayName = random.choice(TITLES)

    if TEST_I18N:
        note.displayName = uw(note.displayName)

    delta = timedelta(days=random.randint(0, 5),
                      hours=random.randint(0, 24))
    note.createdOn = datetime.now(tzinfo) + delta
    note.setTriageStatus(randomEnum(pim.TriageEnum))
    return note

def GenerateTask(view, tzinfo=None):
    """ Generate one Task item """
    task = pim.Task(itsView=view)
    delta = timedelta(days=random.randint(0, 5),
                      hours=random.randint(0, 24))
    task.summary = random.choice(TITLES)

    if TEST_I18N:
        task.summary = uw(task.summary)

    task.itsItem.setTriageStatus(randomEnum(pim.TriageEnum))
    return task.itsItem

def GenerateEventTask(view, days=30, tzinfo=None):
    """ Generate one Task/Event stamped item """
    event = GenerateCalendarEvent(view, days, tzinfo=tzinfo)
    pim.TaskStamp(event).add()
    return event

DOMAIN_LIST = [u'flossrecycling.com', u'flossresearch.org', u'rosegardens.org',
               u'electricbagpipes.com', u'facelessentity.com', u'example.com',
               u'example.org', u'example.net', u'hangarhonchos.org', u'ludditesonline.net']

FIRSTNAMES = [u'Alec', u'Aleks', u'Alexis', u'Amy', u'Andi', u'Andy', u'Aparna',
              u'Bart', u'Blue', u'Brian', u'Bryan', u'Caroline', u'Cedric', u'Chao', u'Chris',
              u'David', u'Donn', u'Ducky', u'Dulcy', u'Erin', u'Esther',
              u'Freada', u'Grant', u'Greg', u'Heikki', u'Hilda',
              u'Jed', u'John', u'Jolyn', u'Jurgen', u'Jae Hee',
              u'Katie', u'Kevin', u'Lisa', u'Lou',
              u'Michael', u'Mimi', u'Mitch', u'Mitchell', u'Morgen',
              u'Pieter', u'Robin', u'Stefanie', u'Stuart', u'Suzette',
              u'Ted', u'Trudy', u'William']

LASTNAMES = [u'Anderson', u'Baillie', u'Baker', u'Botz', u'Brown', u'Burgess',
             u'Capps', u'Cerneka', u'Chang', u'Decker', u'Decrem', u'Denman', u'Desai', u'Dunn', u'Dusseault',
             u'Figueroa', u'Flett', u'Gamble', u'Gravelle',
             u'Hartsook', u'Haurnesser', u'Hernandez', u'Hertzfeld', u'Humpa',
             u'Kapor', u'Klein', u'Kim', u'Lam', u'Leung', u'McDevitt', u'Montulli', u'Moseley',
             u'Okimoto', u'Parlante', u'Parmenter', u'Rosa',
             u'Sagen', u'Sciabica', u'Sherwood', u'Skinner', u'Stearns', u'Sun', u'Surovell',
             u'Tauber', u'Totic', u'Toivonen', u'Toy', u'Tsurutome', u'Vajda', u'Yin']

COLLECTION_NAMES = [u'Scratchings', u'Home', u'Work', u'OSAF', u'Kids', u'School', 
                    u'Book club', u'Wine club', u'Karate', u'Knitting', u'Soccer', 
                    u'Chandler', u'Cosmo', u'Scooby', u'Choir', u'Movies', u'Snowball', 
                    u'Lassie', u'Humor', u'Odds n Ends', u'BayCHI', u'OSCON', u'IETF', 
                    u'Financial', u'Medical', u'Philanthropy']

PHONETYPES = [u'cell', u'voice', u'fax', u'pager']

#area codes not listed as valid at http://www.cs.ucsd.edu/users/bsy/area.html
AREACODES = [311,411,555,611,811,324,335]

def GeneratePhoneNumber():
    areaCode = random.choice(AREACODES)
    exchange = random.randint(220, 999)
    number = random.randint(1000, 9999)
    return u"(%3d) %3d-%4d" % (areaCode, exchange, number)

def GenerateEmailAddress(name):
    domainName = random.choice(DOMAIN_LIST)
    handle = random.choice([name.firstName, name.lastName])
    return u"%s@%s" % (handle.lower(), domainName)

def GenerateEmailAddresses(view, name):
    list = []
    for i in range(random.randint(1, 2)):
        email = Mail.EmailAddress.getEmailAddress(view, 
                                                  GenerateEmailAddress(name))
        list.append(email)
    return list

def GenerateContactName(view):
    name = pim.ContactName(itsView=view)
    name.firstName = random.choice(FIRSTNAMES)
    name.lastName = random.choice(LASTNAMES)

    if TEST_I18N:
        name.firstName = uw(name.firstName)
        name.lastName = uw(name.lastName)

    return name

def GenerateContact(view):
    contact = pim.Contact(itsView=view)
    contact.contactName = GenerateContactName(view)
    return contact

def GenerateCollection(view, existingNames=None):
    collection = pim.SmartCollection(itsView=view)
    schema.ns('osaf.pim', view).mine.addSource(collection)
    
    while True:
        # Find a name that isn't already in use
        potentialName = random.choice(COLLECTION_NAMES)

        if TEST_I18N:
            potentialName = uw(potentialName)

        if existingNames is None or potentialName not in existingNames:
            collection.displayName = potentialName
            if existingNames is not None:
                existingNames.append(potentialName)
            break
        
    schema.ns("osaf.app", view).sidebarCollection.add (collection)
    return collection


def GenerateItems(view, count, function, collections=[], *args, **dict):
    """ 
    Generate 'count' content items using the given function (and args), and
    add them to a subset of the given collections (if given)
    """
    
    # If we were given one collection, we'll add all items to it.
    # If we were given more than one, we'll add each item to (at most) a third
    # of the collections.
    if len(collections) == 1:
        maxCollCount = 1
    else:    
        maxCollCount = (len(collections) / 3)
    
    results = []
    for index in range(count):
        newItem = function(view, *args, **dict)
        
        # Mark the new item "read" most of the time.
        if random.randint(0,3):
            newItem.read = True

        if maxCollCount > 0:
            for index in range(random.randint(0, maxCollCount)):
                collections[random.randint(0, len(collections)-1)].add(newItem)

        results.append(newItem)

    return results

def GenerateAllItems(view, count, sidebarCollection=None, oneCollection=None):
    """ Generate a bunch of items of several types, for testing. """
    
    # If we weren't given one collection, generate some item collections to put them in.
    if oneCollection is None:
        existingNames = sidebarCollection is not None and [ existingCollection.displayName for existingCollection in sidebarCollection] or []
        collections = GenerateItems(view, 6, GenerateCollection, [], existingNames)
    else:
        collections = [oneCollection]
    
    items = []
    defaultTzinfo = view.tzinfo.default
    for fn in GenerateMailMessage, GenerateNote, GenerateCalendarEvent, GenerateTask, GenerateEventTask: # GenerateContact omitted.
        def newFn(*args, **keywds):
            keywds['tzinfo'] = defaultTzinfo
            return fn(*args, **keywds)
        items.append(GenerateItems(view, count, newFn, collections))

    return items
