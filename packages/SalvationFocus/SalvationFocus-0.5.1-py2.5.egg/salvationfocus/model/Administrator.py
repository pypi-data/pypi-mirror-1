#!/usr/bin/env python

#
#  Administrator.py
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

from sqlalchemy import Table, Column, Integer, String, CheckConstraint

class Administrator(object):
    
    def __repr__(self):
        return "<Administrator(%s %s)>" % (self.login_name, self.email)
    
        
        
def get_administrators_table(meta):
    
    administrators_table = Table('administrators', meta,
        Column('id', Integer, primary_key=True),
        Column('login_name', String(30), nullable=False, unique=True),
        Column('password_hash', String(64),
               CheckConstraint('length("password_hash") = 64'),
               nullable=False),
        Column('email', String(50), nullable=False, unique=True),
        mysql_engine='InnoDB'
    )
    
    return administrators_table