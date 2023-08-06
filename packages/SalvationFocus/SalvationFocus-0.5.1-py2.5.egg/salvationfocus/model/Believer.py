#!/usr/bin/env python

#
#  Believer.py
#
#  Created on February 1, 2008
#
#
#
#  Copyright 2008 Todd A. Johnson
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from sqlalchemy import Table, Column, Integer, String, ForeignKey, \
    DateTime, UniqueConstraint

#from datetime import datetime


class Believer(object):
        
    def __repr__(self):
        return "<Believer(%s %s)>" % (self.first_name, self.last_name)

    

def get_believers_table(meta):

    believers_table = Table('believers', meta,
        Column('id', Integer, primary_key=True),
        Column('first_name', String(30), nullable=False),
        Column('last_name', String(30), nullable=False),
        Column('date_entered', DateTime, nullable=False),
        Column('last_viewed', DateTime),
        Column('times_viewed', Integer, default=0),
        Column('submitter_id', Integer, ForeignKey('submitters.id'),
               nullable=False),
        Column('date_answered', DateTime, nullable=False),
        UniqueConstraint('first_name', 'last_name'),
        mysql_engine='InnoDB'
    )
    
    return believers_table