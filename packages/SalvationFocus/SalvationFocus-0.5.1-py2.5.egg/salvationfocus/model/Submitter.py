#!/usr/bin/env python

#
#  Submitter.py
#
#  Created on January 24, 2008
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

from sqlalchemy import Table, Column, Integer, String, UniqueConstraint


class Submitter(object):
    
    def __repr__(self):
        return "<Submitter(%s %s)>" % (self.first_name, self.last_name)
        
        
def get_submitters_table(meta):
    
    submitters_table = Table('submitters', meta,
        Column('id', Integer, primary_key=True),
        Column('first_name', String(30), nullable=False),
        Column('last_name', String(30), nullable=False),
        Column('phone', String(12), nullable=False),
        Column('email', String(50), nullable=False),
        UniqueConstraint('first_name', 'last_name'),
        mysql_engine='InnoDB'
    )
    
    return submitters_table