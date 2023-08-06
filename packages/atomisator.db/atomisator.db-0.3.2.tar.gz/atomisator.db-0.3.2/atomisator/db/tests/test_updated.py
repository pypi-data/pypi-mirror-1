# -*- encoding: utf-8 -*-
# (C) Copyright 2008 Tarek Ziadé <tarek@ziade.org>
""" DB Apis
"""
from datetime import timedelta
from datetime import datetime

from atomisator.db.core import create_entry
from atomisator.db.core import get_entries
from atomisator.db.core import purge_entries
from atomisator.db.session import create_session

def test_updated():

    create_session('sqlite:///:memory:')

    # making sure we update a feed that already exists
    date = datetime.now()
    entry = {'link': 'the link',
             'summary': 'xxx',
             'date': date, 'updated': date,
             'title': 'the title',
             }
    create_entry(entry, commit=True)

    # if we push it again, it won't be added or changed
    create_entry(entry, commit=True) 

    entries = get_entries().all()

    assert len(entries) == 1

    # unless it has been updated
    entry['summary'] = 'changed'
    entry['updated'] = datetime.now()

    create_entry(entry, commit=True)

    entries = get_entries().all()  
    assert len(entries) == 1  
    assert entries[0].summary == 'changed'

    # of course url is the id
    entry['link'] = 'another'
    create_entry(entry, commit=True)
    entries = get_entries().all()
    assert len(entries) == 2

def test_purge_entries():
    create_session('sqlite:///:memory:') 
    date = datetime.now() - timedelta(40)

    entry = {'link': 'the link',
             'summary': 'xxx',
             'date': date, 'updated': date,
             'title': 'the title',
             }
    create_entry(entry, commit=True)
   
    entries = get_entries().all() 
    assert len(entries) == 1

    purge_entries()
    entries = get_entries().all() 
    assert len(entries) == 0



