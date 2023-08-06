from pylons import config
from sqlalchemy import MetaData, desc
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker

#get models
from Prebeliever import Prebeliever, get_prebelievers_table
from Submitter import Submitter, get_submitters_table
from Administrator import Administrator, get_administrators_table
from Believer import Believer, get_believers_table

Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
                                      bind=config['pylons.g'].sa_engine))

metadata = MetaData()

#create the tables if they don't already exist
#metadata.create_all(bind=self.db.engine)

admin_table = get_administrators_table(metadata)
submit_table = get_submitters_table(metadata)
pre_table = get_prebelievers_table(metadata)
believer_table = get_believers_table(metadata)

mapper(Administrator, admin_table, order_by=[admin_table.columns.login_name])
mapper(Submitter, submit_table, properties=
        {
            'prebelievers':relation(Prebeliever,
                                    cascade="all, delete",
                                    backref='submitter')
        },
        order_by=[submit_table.columns.last_name,
                  submit_table.columns.first_name]
    )
mapper(Prebeliever, pre_table, order_by=[pre_table.columns.last_name,
                                         pre_table.columns.first_name])
mapper(Believer, believer_table, order_by=[believer_table.columns.last_name,
                                           believer_table.columns.first_name])