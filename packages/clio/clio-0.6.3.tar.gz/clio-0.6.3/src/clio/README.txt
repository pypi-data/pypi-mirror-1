Clio
====

Clio is a system that builds on SQLAlchemy to support a simple
workflow and history system. A Clio table is a table that has workflow
status column and a code column. The code column uniquely identifies
the record over multiple versions. It should not be confused with the
id column, which describes versions that may be at different stages in
a workflow.

SQLALchemy setup
----------------

First we'll set up the database::

  >>> from sqlalchemy import create_engine, MetaData

  >>> engine = create_engine('mysql:///clio_tests')

  >>> metadata = MetaData()

Let's also set up an ORM session::

  >>> from sqlalchemy.orm import sessionmaker
  >>> Session = sessionmaker(bind=engine)
  >>> session = Session()

Table and class
---------------

Let's define and create a simple table that is workflowed::

  >>> from sqlalchemy import Table, Column, Integer, Unicode, UniqueConstraint
  >>> user = Table(
  ...   'user', metadata,
  ...   Column('id', Integer, primary_key=True),
  ...   Column('code', Integer, nullable=False),
  ...   Column('status', Integer, nullable=False),
  ...   Column('username', Unicode(50), nullable=False),
  ...   Column('full_name', Unicode(50), nullable=False),
  ...   UniqueConstraint('code', 'status', name="workflow"),
  ...   )
  >>> metadata.create_all(engine)

We will also map this table to a class::
  
  >>> import clio
  >>> from sqlalchemy.orm import mapper
  >>> user_counter = 0
  >>> class User(clio.Model):
  ...     def __init__(self, username, full_name):
  ...         global user_counter
  ...         super(User, self).__init__(user_counter)
  ...         user_counter += 1
  ...         self.username = username
  ...         self.full_name = full_name
  >>> dummy = mapper(User, user)

Note: we simulate auto_increment behavior with user_counter here. This
is to maintain codes. XXX test whether this works properly with MySQL

Creation
--------

We can now create a new user::

  >>> faassen = User(u'faassen', u"Martijn Faassen")
  >>> session.add(faassen)
  >>> session.flush()

  >>> [user.username for user in session.query(User)]
  [u'faassen']

The user has a status NEW::

  >>> faassen.status is clio.NEW
  True

We are free to update the user's data::

  >>> faassen.full_name = u"The Other Faassen"
  >>> session.flush()

Publishing
----------

We can now publish the user::
  
  >>> faassen = faassen.publish()
  >>> session.flush()

Once an object is published, we cannot just change it::

  XXX To be implemented

Editing 
-------

To change the object, we need to create an editable version::

  >>> faassen_editable = faassen.edit()

We can now change the editable version::

  >>> faassen_editable.full_name = u"Martijn Faassen"

If we ask for the editable again, we get the same object::

  >>> second_editable = faassen.edit()
  >>> second_editable is faassen_editable
  True

Getting an editable version of an editable version gives the same object
back::
  
  >>> faassen_editable_again = faassen_editable.edit()
  >>> faassen_editable_again is faassen_editable
  True

Making editable somethign that has foreign key dependencies on it:
also make those editable.

We can publish the editable version again::

  >>> faassen = faassen_editable.publish()
  >>> session.flush()

The editable version is now published::

  >>> faassen_editable.status is clio.PUBLISHED
  True
  >>> faassen is faassen_editable
  True

Relations
---------

We set up a role table that is related by a foreign key relationship to
the user table. A user (of, say, a game) may have zero or more characters in
the game::

  >>> from sqlalchemy import ForeignKey
  >>> character = Table(
  ...   'charac', metadata,
  ...   Column('id', Integer, primary_key=True),
  ...   Column('code', Integer, nullable=False),
  ...   Column('status', Integer, nullable=False),
  ...   Column('name', Unicode(50), nullable=False),
  ...   Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
  ...   )
  >>> metadata.create_all(engine)

We'll map this to a class::
  
  >>> character_counter = 0
  >>> class Character(clio.Model):
  ...     def __init__(self, name):
  ...         global character_counter
  ...         super(Character, self).__init__(character_counter)
  ...         character_counter += 1
  ...         self.name = name
  >>> from sqlalchemy.orm import relation
  >>> dummy = mapper(Character, character,
  ...                properties={'user': relation(User, backref='characters')})

  >>> clio.workflow_properties(User)
  >>> clio.workflow_properties(Character)

We can now add characters to a user::

  >>> faassen_editable = faassen.edit()
  >>> faassen_editable.characters.append(Character(u'Wibbit'))
  >>> faassen_editable.characters.append(Character(u'Niyura'))

The non-editable version has no characters::

  >>> faassen.characters
  []

The editable version does, however::

  >>> len(faassen_editable.characters)
  2

We will publish the editable version now::

  >>> faassen = faassen_editable.publish()

The old editable version is now the published version::

  >>> faassen.status is clio.PUBLISHED
  True

The published version will have two characters now::

  >>> len(faassen.characters)
  2

When we make a new editable version, it should also have these characters::

  >>> faassen_editable = faassen.edit()
  >>> len(faassen_editable.characters)
  2

The published version should still have two characters::

  >>> len(faassen.characters)
  2


