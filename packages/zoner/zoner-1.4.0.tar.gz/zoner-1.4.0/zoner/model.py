from datetime import datetime

from turbogears.database import metadata, mapper, session
from turbogears import identity 

# import some basic SQLAlchemy classes for declaring the data model
# (see http://www.sqlalchemy.org/docs/04/ormtutorial.html)
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relation
# import some datatypes for table columns from SQLAlchemy
# (see http://www.sqlalchemy.org/docs/04/types.html for more)
from sqlalchemy import String, Unicode, Integer, DateTime, CHAR, desc


# The identity schema.
visits_table = Table('visit', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('created', DateTime, nullable=False, default=datetime.now),
    Column('expiry', DateTime)
)

visit_identity_table = Table('visit_identity', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('user_id', Integer, ForeignKey('tg_user.user_id'), index=True)
)

groups_table = Table('tg_group', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now)
)

users_table = Table('tg_user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', Unicode(16), unique=True),
    Column('email_address', Unicode(255), unique=True),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(40)),
    Column('created', DateTime, default=datetime.now)
)

permissions_table = Table('permission', metadata,
    Column('permission_id', Integer, primary_key=True),
    Column('permission_name', Unicode(16), unique=True),
    Column('description', Unicode(255))
)

user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id')),
    Column('group_id', Integer, ForeignKey('tg_group.group_id'))
)

group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id')),
    Column('permission_id', Integer, ForeignKey('permission.permission_id'))
)

# constants for change_history.change_type values
CHANGE_TYPE_SAVE = 'S'
CHANGE_TYPE_RELOAD = 'R'
CHANGE_TYPE_REVERT = 'V'
CHANGE_TYPES = (CHANGE_TYPE_SAVE, CHANGE_TYPE_RELOAD, CHANGE_TYPE_REVERT)

change_history_table = Table('change_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('zone', Unicode(256), nullable=False, index=True),
    Column('user', Integer, ForeignKey('tg_user.user_id')),
    Column('timestamp', DateTime, nullable=False, default=datetime.now),
    Column('serial', Integer, nullable=False),          # the Zone serial from SOA
    Column('change_type', CHAR(1), nullable=False),     # one of: "S"ave, "R"eload
    Column('archived_name', Unicode(256)),              # only for type "S"ave
)


class Visit(object):
    """
    A visit to your site
    """
    def lookup_visit(cls, visit_key):
        return Visit.query.get(visit_key)
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(object):
    """
    A Visit that is link to a User object
    """
    pass

class Group(object):
    """
    An ultra-simple group definition.
    """
    pass

class User(object):
    """
    Reasonably basic User definition. Probably would want additional
    attributes.
    """
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    permissions = property(permissions)

class Permission(object):
    """
    A relationship that determines what each Group can do
    """
    pass

class ChangeHistory(object):
    """Tracks all changes made to a zone.
    """
    def timestamp_format(self, format):
        return self.timestamp.strftime(format)
    
    def user_object(self):
        return User.query().filter_by(user_id=self.user).one()
    
    def history_records(cls, zone):
        return cls.query.filter_by(zone=zone)
    history_records = classmethod(history_records)
    


mapper(Visit, visits_table)
mapper(VisitIdentity, visit_identity_table,
    properties=dict(users=relation(User, backref='visit_identity'))
)
mapper(User, users_table)
mapper(Group, groups_table,
    properties=dict(users=relation(User, secondary=user_group_table, backref='groups'))
)
mapper(Permission, permissions_table,
    properties=dict(groups=relation(Group, secondary=group_permission_table, backref='permissions'))
)

mapper(ChangeHistory, change_history_table,
    properties=dict(users=relation(User, backref='change_history'))
    # extension=SelectResultsExt()
)

