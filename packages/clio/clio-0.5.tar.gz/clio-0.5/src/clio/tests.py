import unittest, doctest
from datetime import datetime, timedelta

import clio

from sqlalchemy import MetaData, create_engine
from sqlalchemy import Table, Column, Integer, Unicode
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, dynamic_loader, sessionmaker, backref
from sqlalchemy import and_, or_

metadata = MetaData()

# a table a that has b referencing it
a = clio.Table(
    'a', metadata,
    Column('message', Unicode(50), nullable=False),
    mysql_engine='InnoDB',
    )

# a table b referencing a
b = clio.Table(
    'b', metadata,
    Column('message', Unicode(50), nullable=False),
    Column('a_id', Integer, ForeignKey('a.id'), nullable=False),
    mysql_engine='InnoDB',
    )

# c and d point to each other in a many to many relationship
c = clio.Table(
    'c', metadata,
    Column('message', Unicode(50), nullable=False),
    mysql_engine='InnoDB',
    )

d = clio.Table(
    'd', metadata,
    Column('message', Unicode(50), nullable=False),
    mysql_engine='InnoDB',
    )

# this isn't a clio table
c_d = Table(
    'c_d', metadata,
    Column('c_id', Integer, ForeignKey('c.id'), nullable=False),
    Column('d_id', Integer, ForeignKey('d.id'), nullable=False),
    mysql_engine='InnoDB',
     )

a_code = clio.Sequence('a_code', metadata)

class A(clio.Model):
    def __init__(self, code, message):
        super(A, self).__init__(code)
        self.message = message

    def _now(self):
        # Override this to run with a faster clock
        return now()

b_code = clio.Sequence('b_code', metadata)

class B(clio.Model):
    def __init__(self, code, message):
        super(B, self).__init__(code)
        self.message = message

    def _now(self):
        # Override this to run with a faster clock
        return now()

c_code = clio.Sequence('c_code', metadata)

class C(clio.Model):
    def __init__(self, code, message):
        super(C, self).__init__(code)
        self.message = message

    def _now(self):
        # Override this to run with a faster clock
        return now()
    
d_code = clio.Sequence('d_code', metadata)

class D(clio.Model):
    def __init__(self, code, message):
        super(D, self).__init__(code)
        self.message = message

    def _now(self):
        # Override this to run with a faster clock
        return now()

mapper(A, a,
       properties={
        'bs': dynamic_loader(B,
                             cascade='all, delete',
                             backref='a'),
        }
       )
mapper(B, b)

mapper(C, c)

mapper(D, d,
       properties={
        'cs': dynamic_loader(C,
                             secondary=c_d,
                             backref=backref('ds', lazy='dynamic')),

        })

clio.workflow_properties(A)
clio.workflow_properties(B)
clio.workflow_properties(C)
clio.workflow_properties(D)

_first_dt = datetime.now()

def now():
    """A special "now" where time runs much faster than normal.

    This is necessary to properly test storage of datetimes in
    a relational database, which only works with a second-granularity.
    """
    delta = datetime.now() - _first_dt
    delta *= 100000
    return _first_dt + delta

class ClioTestCase(unittest.TestCase):
    def setUp(self):
        engine = create_engine('mysql:///clio_tests', echo=False)
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.session.query(B).delete()
        self.session.query(A).delete()
        self.session.execute(c_d.delete())
        self.session.query(C).delete()
        self.session.query(D).delete()
        self.session.flush()
        self.session.commit()
        
    def tearDown(self):
        self.session.commit()

    def _get_published(self):
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one = one.publish()
        self.session.commit()
        return one

    def _get_editable(self):
        one = self._get_published()
        one_editable = one.edit()
        self.session.commit()
        return one_editable

    def _get_updatable(self):
        one = self._get_published()
        one_updatable = one.update()
        self.session.commit()
        return one_updatable
        
    def _get_rel_published(self):
        one = A(a_code(self.session), u'One')
        one.bs.append(B(b_code(self.session), u'B1'))
        one.bs.append(B(b_code(self.session), u'B2'))
        self.session.add(one)
        one = one.publish()
        self.session.commit()
        return one

    def _get_rel_editable(self):
        one = self._get_rel_published()
        one_editable = one.edit()
        self.session.commit()
        return one_editable

    def _get_rel_updatable(self):
        one = self._get_rel_published()
        one_updatable = one.update()
        self.session.commit()
        return one_updatable

    def test_a_new(self):
        """Create a new A.
        """
        one = A(a_code(self.session), u"One")
        self.assertEquals(clio.NEW, one.status)

    def test_a_new_time(self):
        """Create a new A.
        """
        before = now()
        one = A(a_code(self.session), u"One")
        after = now()

        self.assert_(before < one.creation_timestamp < after)
        self.assert_(before < one.workflow_timestamp < after)

    def test_a_new_change(self):
        """We can change new A.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        self.session.commit()

        one.message = u"One New Message"
        self.session.commit()

    def test_a_publish(self):
        """We can publish a new A.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one = one.publish()
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_publish_time(self):
        """We can publish a new A.
        """
        before_create = now()
        one = A(a_code(self.session), u'One')
        after_create = now()
        self.session.add(one)

        before_publish = now()
        one = one.publish()
        after_publish = now()

        self.assert_(
            before_create < one.creation_timestamp < after_create)
        self.assert_(
            before_publish < one.workflow_timestamp < after_publish)

    def test_cannot_change_published(self):
        pass # to be implemented
        
    def test_a_edit(self):
        """We can edit a published A.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one = one.publish()
        self.session.commit()

        one_editable = one.edit()
        one_editable.message = u'One New Message'
        self.session.commit()

    def test_a_edit_time(self):
        """We can edit a published A.
        """
        before_create = now()
        one = A(a_code(self.session), u'One')
        after_create = now()
        self.session.add(one)
        self.session.commit()

        before_publish = now()
        one = one.publish()
        after_publish = now()
        
        self.session.commit()
        
        before_edit = now()
        one_editable = one.edit()
        after_edit = now()        

        self.assert_(before_create < one.creation_timestamp < after_create)
        self.assert_(before_publish < one.workflow_timestamp < after_publish)
        self.assert_(
            before_edit < one_editable.workflow_timestamp < after_edit)
        self.assert_(
            before_edit < one_editable.creation_timestamp < after_edit)

    def test_a_update(self):
        """We can update a published A.

        Since there are no relations, this should be equivalent to editing it.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one = one.publish()
        self.session.commit()

        one_updatable = one.update()
        one_updatable.message = u'One New Message'
        self.session.commit()

    def test_a_update_time(self):
        """We can update a published A.
        """
        before_create = now()
        one = A(a_code(self.session), u'One')
        after_create = now()
        self.session.add(one)
        self.session.commit()

        before_publish = now()
        one = one.publish()
        after_publish = now()
        
        self.session.commit()
        
        before_update = now()
        one_updatable = one.update()
        after_update = now()        

        self.assert_(before_create < one.creation_timestamp < after_create)
        self.assert_(before_publish < one.workflow_timestamp < after_publish)
        self.assert_(
            before_update < one_updatable.workflow_timestamp < after_update)
        self.assert_(
            before_update < one_updatable.creation_timestamp < after_update)

    def test_a_publish_editable(self):
        """We can publish an edited A.
        """
        one_editable = self._get_editable()
        one = one_editable.publish()
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_publish_editable_time(self):
        """We can publish an edited A.
        """
        one_editable = self._get_editable()
        
        before_publish = now()
        one = one_editable.publish()
        after_publish = now()
        self.assert_(before_publish < one.workflow_timestamp < after_publish)

    def test_a_publish_updatable(self):
        """We can publish an updatable A.

        Should be equivalent to test_a_publish_updatable as there
        are no relations.
        """
        one = self._get_published()
        one_updatable = one.update()
        self.session.commit()

        one = one_updatable.publish()
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_publish_deleted(self):
        """We can publish an object set DELETED.
        """
        one = self._get_published()
        one_deleted = one.delete()

        one_published = one_deleted.publish()
        self.assert_(one.is_archived())
        self.assert_(one_published.is_archived())
        
    def test_a_publish_published_under_edit(self):
        """We can publish an object set PUBLISHED_UNDER_EDIT.
        This simply is publishing the editable version.
        """
        one = self._get_published()
        one_editable = one.edit()
        one.publish()
        self.assertEquals(clio.PUBLISHED, one_editable.status)
        self.assert_(one.is_archived())

    def test_a_publish_published_under_update(self):
        """We can publish an object set PUBLISHED_UNDER_UPDATE.
        This simply is publishing the updatable version.
        """
        one = self._get_published()
        one_editable = one.update()
        one.publish()
        self.assertEquals(clio.PUBLISHED, one_editable.status)
        self.assert_(one.is_archived())

    def test_a_publish_published(self):
        """We can publish a PUBLISHED object. Nothing happens.
        """
        one = self._get_published()
        one_published = one.publish()
        
        self.assertEquals(one_published, one)
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_archive(self):
        """When we publish an edited A, the previous version is archived.
        """
        one1 = self._get_published()
        one_editable2 = one1.edit()
        one_editable2.message = u'One 2'
        one2 = one_editable2.publish()
        one_editable3 = one2.edit()
        one_editable3.message = u'One 3'
        one3 = one_editable3.publish()

        self.assert_(one1.is_archived())
        self.assertEquals('One', one1.message)
        self.assert_(one2.is_archived())
        self.assertEquals('One 2', one2.message)
        self.assertEquals(clio.PUBLISHED, one3.status)
        self.assertEquals('One 3', one3.message)

    def test_a_archive_time(self):
        """When we publish an edited A, the previous version is archived.
        """
        one1 = self._get_published()
        one_editable2 = one1.edit()
        one_editable2.message = u'One 2'
        before_publish1 = now()
        one2 = one_editable2.publish()
        after_publish1 = now()
        one_editable3 = one2.edit()
        one_editable3.message = u'One 3'
        before_publish2 = now()
        one3 = one_editable3.publish()
        after_publish2 = now()

        self.assert_(
            before_publish1 < one1.workflow_timestamp < after_publish1)
        self.assert_(
            before_publish2 < one2.workflow_timestamp < after_publish2)
        self.assert_(
            before_publish2 < one3.workflow_timestamp < after_publish2)

    def test_a_archive_updatable(self):
        """When we publish an updated, the previous version is archived.

        Should be equivalent to test_a_archive()
        """
        one1 = self._get_published()
        one_updatable2 = one1.update()
        one_updatable2.message = u'One 2'
        one2 = one_updatable2.publish()
        one_updatable3 = one2.update()
        one_updatable3.message = u'One 3'
        one3 = one_updatable3.publish()
        
        self.assert_(one1.is_archived())
        self.assertEquals('One', one1.message)
        self.assert_(one2.is_archived())
        self.assertEquals('One 2', one2.message)
        self.assertEquals(clio.PUBLISHED, one3.status)
        self.assertEquals('One 3', one3.message)

    def test_a_edit_twice(self):
        """If we edit the published A twice, the second one is the
        same as the first.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable2 = one.edit()
        self.assert_(one_editable is one_editable2)

    def test_a_edit_new(self):
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one_editable = one.edit()

    def test_a_update_twice(self):
        """If we update the published A twice, the second one is the same
        as the first.
        """
        one = self._get_published()
        one_updatable = one.update()
        one_updatable2 = one.update()
        self.assert_(one_updatable is one_updatable2)
        
    def test_a_edit_editable(self):
        """Editing something editable gives the same object back.
        """
        one_editable = self._get_editable()
        one_editable_again = one_editable.edit()
        self.assert_(one_editable_again is one_editable)

    def test_a_update_updatable(self):
        """Updating an updatable gives the same object back.
        """
        one_updatable = self._get_updatable()
        one_updatable_again = one_updatable.update()
        self.assert_(one_updatable_again is one_updatable)

    def test_a_update_editable(self):
        one_editable = self._get_editable()
        self.assertRaises(clio.UpdateError, one_editable.update)

    def test_a_edit_updatable(self):
        one_updatable = self._get_updatable()
        self.assertRaises(clio.EditError, one_updatable.edit)

    def test_a_edit_archived(self):
        one = self._get_published()
        one_editable = one.edit()
        one2 = one_editable.publish()
        self.assert_(one.is_archived())
        self.assertRaises(clio.EditError, one.edit)

    def test_a_update_archived(self):
        one = self._get_published()
        one_editable = one.update()
        one2 = one_editable.publish()
        self.assert_(one.is_archived())
        self.assertRaises(clio.UpdateError, one.update)

    def test_a_edit_deleted(self):
        one = self._get_published()
        one_deleted = one.delete()
        one_editable = one_deleted.edit()
        self.assertEquals(clio.EDITABLE, one_editable.status)
        self.assertEquals(clio.PUBLISHED_UNDER_EDIT, one.status)
        
    def test_a_update_deleted(self):
        one = self._get_published()
        one_deleted = one.delete()
        one_editable = one_deleted.update()
        self.assertEquals(clio.UPDATABLE, one_editable.status)
        self.assertEquals(clio.PUBLISHED_UNDER_UPDATE, one.status)
        
    def test_a_rel_new(self):
        """We create an A with a relation (Bs).
        """
        one = A(a_code(self.session), u"One")
        one.bs.append(B(b_code(self.session), u'B1'))
        one.bs.append(B(b_code(self.session), u'B2'))
        self.session.add(one)
        
        self.assertEquals(clio.NEW, one.status)
        self.assertEquals(clio.NEW, one.bs[0].status)
        self.assertEquals(clio.NEW, one.bs[1].status)
        
        # all bs are editable
        self.assertEquals(list(one.bs), list(one.bs_editable))
        # no bs are archived
        self.assertEquals([], list(one.bs_archived))
        # there are no published bs yet
        self.assertEquals([], list(one.bs_published))
    
    def test_a_rel_new_edit(self):
        """We edit an object with relations.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one.bs.append(B(b_code(self.session), u'B1'))
        one.bs.append(B(b_code(self.session), u'B2'))

        self.session.commit()

        one.message = u"One New Message"
        one.bs_editable[0].message = u'B1 new'

        self.session.commit()

    def test_a_rel_publish(self):
        """We publish an object with relations.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        one.bs.append(B(b_code(self.session), u'B1'))
        one.bs.append(B(b_code(self.session), u'B2'))
         
        self.assertEquals(list(one.bs), list(one.bs_editable))
        self.assertEquals([], list(one.bs_archived))
        self.assertEquals([], list(one.bs_published))

        one = one.publish()
        
        self.assertEquals(clio.PUBLISHED, one.status)
        self.assertEquals(clio.PUBLISHED, one.bs[0].status)
        self.assertEquals(clio.PUBLISHED, one.bs[1].status)
        
        self.assertEquals(list(one.bs), list(one.bs_published))
        self.assertEquals([], list(one.bs_archived))
        self.assertEquals(list(one.bs_published), list(one.bs_editable))
        
    def test_a_rel_edit(self):
        """We make editable an object with relations that was published.
        """
        one = self._get_rel_published()
        one_editable = one.edit()
        one_editable.message = u'One New Message'
        self.session.commit()

    def test_a_rel_update(self):
        """We make updatable an object with relations that was published.
        """
        one = self._get_rel_published()
        one_updatable = one.update()
        one_updatable.message = u'One New Message'
        self.session.commit()

    def test_a_rel_update_retain_relations(self):
        """When we update a version, it retains the relations of the
        published version.
        """
        one = self._get_rel_published()
        one_updatable = one.update()
        self.assertEquals(2, len(list(one_updatable.bs)))
        
    def test_a_rel_publish_editable(self):
        """We publish again an object made editable.
        """
        one_editable = self._get_rel_editable()
        one = one_editable.publish()
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_rel_publish_updatable(self):
        """We publish again an object made updatable.
        """
        one_updatable = self._get_rel_updatable()
        one = one_updatable.publish()
        self.assertEquals(clio.PUBLISHED, one.status)

    def test_a_rel_update_archive(self):
        """By publishing again, we create archived objects.
        The relations stay with the published version.
        """
        one1 = self._get_rel_published()
        one_updatable2 = one1.update()
        one_updatable2.message = u'One 2'
        one2 = one_updatable2.publish()
        one_updatable3 = one2.update()
        one_updatable3.message = u'One 3'
        one3 = one_updatable3.publish()
        
        self.assert_(one1.is_archived())
        self.assertEquals([], list(one1.bs))
        
        self.assertEquals('One', one1.message)
        
        self.assert_(one2.is_archived())
        self.assertEquals([], list(one2.bs))

        self.assertEquals(clio.PUBLISHED, one3.status)
        self.assert_(clio.PUBLISHED, one3.bs[0].status)
        self.assert_(clio.PUBLISHED, one3.bs[1].status)

        self.assertEquals('One 3', one3.message)
        
    def test_a_rel_archive(self):
        """By publishing again, we create archived objects.
        """
        one1 = self._get_rel_published()
        one_editable2 = one1.edit()
        one_editable2.message = u'One 2'
        one2 = one_editable2.publish()
        one_editable3 = one2.edit()
        one_editable3.message = u'One 3'
        one3 = one_editable3.publish()
       
        self.assert_(one1.is_archived())
        self.assert_(one1.bs[0].is_archived())
        self.assert_(one2.bs[1].is_archived())
        self.assertEquals('One', one1.message)
        
        self.assert_(one2.is_archived())
        self.assert_(one2.bs[0].is_archived())
        self.assert_(one2.bs[1].is_archived())
        self.assertEquals('One 2', one2.message)
        
        self.assertEquals(clio.PUBLISHED, one3.status)
        self.assert_(clio.PUBLISHED, one3.bs[0].status)
        self.assert_(clio.PUBLISHED, one3.bs[1].status)

        self.assertEquals('One 3', one3.message)

    def test_a_rel_publish_editable_relation(self):
        """We have an object, previously published.

        We make its relation editable.
        Now we make the object editable.
        Now we publish.
        """
        one = self._get_rel_published()
        b0 = one.bs[0]
        b0_editable = b0.edit()
        one_editable = one.edit()
        one_published = one_editable.publish()

        self.assertEquals(2, len(list(one_published.bs_published)))

    def test_a_rel_publish_from_new(self):
        """We have a relation that is on a new object.
        We can't publish just the relation.
        """
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        b1 = B(b_code(self.session), u'Alpha')
        one.bs.append(b1)
        self.assertRaises(clio.PublishError, b1.publish)

    def test_a_rel_delete(self):
        one = self._get_rel_published()
        deleted = one.delete()

        self.assertEquals(clio.DELETED, deleted.status)
        self.assertEquals(clio.DELETED, deleted.bs_editable[0].status)
        self.assertEquals(2, len(
                self.session.query(B).filter(B.status == clio.DELETED).all()))
        self.assertEquals(2, len(
                self.session.query(B).filter(B.status == clio.PUBLISHED_UNDER_DELETE).all()))

        deleted.publish()
        self.assertEquals(clio.ARCHIVED, one.status)

        self.assertEquals(2, len(list(one.bs_archived)))
        # we shouldn't have anything of these statuses
        self.assertEquals(0, len(
                self.session.query(B).filter(B.status == clio.PUBLISHED).all()))

    def test_a_rel_delete_editable(self):
        one = self._get_rel_published()
        editable = one.edit()
        deleted = editable.delete()

        self.assertEquals(clio.DELETED_EDITABLE,
                          deleted.status)
        self.assertEquals(clio.DELETED_EDITABLE,
                          deleted.bs_editable[0].status)
        self.assertEquals(2, len(
                self.session.query(B).filter(B.status == clio.DELETED_EDITABLE).all()))
        self.assertEquals(2, len(
                self.session.query(B).filter(B.status == clio.PUBLISHED_UNDER_DELETE).all()))
        
        deleted.publish()
        self.assertEquals(clio.ARCHIVED, one.status)

        self.assertEquals(2, len(list(one.bs_archived)))
        # we shouldn't have anything of these statuses
        self.assertEquals(0, len(
                self.session.query(B).filter(B.status == clio.PUBLISHED).all()))
        self.assertEquals(0, len(
                self.session.query(B).filter(B.status == clio.EDITABLE).all()))
        self.assertEquals(0, len(
                self.session.query(B).filter(B.status == clio.PUBLISHED_UNDER_EDIT).all()))

    def test_a_revert_new(self):
        one = A(a_code(self.session), u"One")
        self.session.add(one)
        self.session.flush()
        one.revert()
        self.assertEquals([], list(self.session.query(A)))

    def test_a_revert_editable(self):
        one = self._get_rel_published()
        one2 = one.edit()
        one3 = one2.revert()
        self.assertEquals(clio.EDITABLE, one3.status)
        self.assertEquals(2, len(list(one3.bs)))
        self.assertEquals(clio.EDITABLE, one3.bs[0].status)
        
    def test_a_revert_deleted(self):
        one = self._get_rel_published()
        one2 = one.delete()
        one3 = one2.revert()
        self.assertEquals(one3, one)
        self.assertEquals(clio.PUBLISHED, one3.status)
        self.assertEquals(2, len(list(one3.bs)))
        
    def test_a_revert_published(self):
        one = self._get_rel_published()
        one2 = one.revert()
        self.assertEquals(one2, one)
        self.assertEquals(clio.PUBLISHED, one.status)
        self.assertEquals(2, len(list(one2.bs)))
        
    def test_a_revert_archived(self):
        one = self._get_published()
        editable = one.edit()
        published2 = editable.publish()
        self.assertRaises(clio.RevertError, one.revert)

    def test_a_rel_revert_new(self):
        one = self._get_rel_published()
        b3 = B(b_code(self.session), u"B3")
        one.bs.append(b3)
        self.session.flush()
        self.assertEquals(3, len(list(one.bs)))
        b3.revert()
        self.assertEquals(2, len(list(one.bs)))
        
    def test_a_rel_revert_editable(self):
        one = self._get_rel_published()
        b1_editable = one.bs[0].edit()
        b1_editable.message = u"changed"
        b1_reverted = b1_editable.revert()
        self.assertEquals(one, b1_reverted.a)
        self.assertEquals(2, len(list(one.bs_editable)))
        sorted_editable = sorted(one.bs_editable, key=lambda o: o.message)
        self.assertEquals("B1", sorted_editable[0].message)
        self.assertEquals(b1_reverted, sorted_editable[0])
        self.assertEquals(clio.EDITABLE, sorted_editable[0].status)
      
    def test_a_rel_revert_deleted(self):
        one = self._get_rel_published()
        b1_deleted = one.bs[0].delete()
        b1_reverted = b1_deleted.revert()
        self.assertEquals(clio.PUBLISHED, one.bs[0].status)
        
    def test_a_rel_revert_published(self):
        one = self._get_rel_published()
        b1_reverted = one.bs[0].revert()
        self.assertEquals(clio.PUBLISHED, one.bs[0].status)
        
    def test_a_rel_revert_relation_on_editable(self):
        one = self._get_rel_published()
        one_editable = one.edit()
        one_editable.bs_editable[0].message = u"changed"
        b1_reverted = one_editable.bs_editable[0].revert()
        self.session.flush()
        self.assertEquals(2, len(list(one_editable.bs_editable)))
        self.assertEquals("B1", one_editable.bs_editable[0].message)

    def test_a_rel_revert_delete_on_editable(self):
        one = self._get_rel_published()
        one_editable = one.edit()
        one_editable.bs_editable[0].delete()
        b1_reverted = one_editable.bs_editable[0].revert()
        self.session.flush()
        self.assertEquals(clio.EDITABLE, one_editable.bs_editable[0].status)
        self.assertEquals(2, len(list(one_editable.bs_editable)))
        self.assertEquals("B1", one_editable.bs_editable[0].message)

    def test_a_rel_revert_recursive_delete(self):
        one = self._get_rel_published()
        one_deleted = one.delete()
        one_reverted = one_deleted.revert()
        self.session.flush()
        self.assertEquals(clio.PUBLISHED, one_reverted.bs[0].status)

    def test_a_rel_revert_cursive_deleted_editable(self):
        one = self._get_rel_published()
        one_editable = one.edit()
        self.assertEquals(clio.EDITABLE, one_editable.bs[0].status)
        one_deleted = one_editable.delete()
        one_reverted = one_deleted.revert()
        self.session.flush()
        self.assertEquals(2, len(list(one_reverted.bs)))
        self.assertEquals(clio.EDITABLE, one_reverted.bs[0].status)
        
    def test_one_to_many_relation_edit(self):
        """We adding relations to a previously published object.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))

        self.assertEquals([], list(one.bs))
        
        self.assertEquals(2, len(list(one_editable.bs_editable)))
        self.assertEquals(clio.EDITABLE, one_editable.status)
        self.assertEquals(clio.NEW, one_editable.bs[0].status)
        self.assertEquals(clio.NEW, one_editable.bs[1].status)

        self.assertEquals(list(one_editable.bs),
                          list(one_editable.bs_editable))
        self.assertEquals([], list(one_editable.bs_archived))
        self.assertEquals([], list(one_editable.bs_published))
        
    def test_one_to_many_relation_publish(self):
        """We publish relations that were previously added.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))
        one = one_editable.publish()
        
        self.assertEquals(clio.PUBLISHED, one.status)
        self.assertEquals(2, len(list(one.bs_published)))
        self.assertEquals(clio.PUBLISHED, one.bs_published[0].status)
        self.assertEquals(clio.PUBLISHED, one.bs_published[1].status)
        
        self.assertEquals(list(one.bs),
                          list(one.bs_published))
        self.assertEquals(list(one.bs),
                          list(one.bs_editable))
        self.assertEquals([],
                          list(one.bs_archived))

    def test_one_to_many_relation_edit_again(self):
        """We re-edit an object with relations.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))

        one = one_editable.publish()

        one_editable_again = one.edit()

        # the newly edited object has two objects under edit
        self.assertEquals(2, len(list(one_editable_again.bs_editable)))
        # the original object has 2 published relations
        self.assertEquals(2, len(list(one.bs_published)))

        # the original object has 2 relations overall
        self.assertEquals(2, len(list(one.bs)))
        self.assertEquals([],
                          list(one.bs_archived))
        self.assertEquals(0,
                          len(list(one.bs_editable)))
        
        self.assertEquals(2,
                          len(list(one_editable_again.bs_editable)))
        self.assertEquals(0,
                          len(list(one_editable_again.bs_archived)))
        self.assertEquals(0,
                          len(list(one_editable_again.bs_published)))

    def test_one_to_many_relation_content_edit(self):
        """We edit relations of a previously published object.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))

        one2 = one_editable.publish()
        one_editable_again = one2.edit()
       
        one_editable_again.bs[0].message = u'B1 edited'
        one_editable_again.bs[1].message = u'B2 edited'

        one3 = one_editable_again.publish()
        
        self.session.commit()
        
        self.assertEquals(u'B1', one2.bs_archived[0].message)
        self.assertEquals(u'B2', one2.bs_archived[1].message)

        self.assertEquals(u'B1 edited', one3.bs[0].message)
        self.assertEquals(u'B2 edited', one3.bs[1].message)

    def test_one_to_many_relation_relation_edit(self):
        """We edit an individual relation and publish it.
        """
        one = self._get_published()
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))

        one2 = one_editable.publish()
        
        # take an individual relation under edit
        b1 = one2.bs[0]
        b2 = one2.bs[1]

        b1_editable = b1.edit()
        
        self.assertEquals(3, len(list(one2.bs)))
        
        self.assertEquals(clio.EDITABLE, b1_editable.status)

    def test_one_to_many_relation_relation_edit_publish(self):
        """We edit a single published relation, and publish it again.
        """
        one = self._get_published()

        # we create two related objects, B1 and B2 and publish this
        one_editable = one.edit()
        one_editable.bs.append(B(b_code(self.session), u'B1'))
        one_editable.bs.append(B(b_code(self.session), u'B2'))
        one2 = one_editable.publish()
        
        # now we take an individual relation under edit and change it
        b1 = one2.bs[0]
        b1_editable = b1.edit()
        b1_editable.message = u"B1 edited"
        
        # we have three related objects now, one editable
        self.assertEquals(3, len(list(one2.bs)))
        self.assertEquals(1, count_status(one2.bs, clio.EDITABLE))
        self.assertEquals(1, count_status(one2.bs, clio.PUBLISHED))
        self.assertEquals(1, count_status(one2.bs, clio.PUBLISHED_UNDER_EDIT))
        
        # in other words...
        self.assertEquals(0, len(list(one2.bs_archived)))
        self.assertEquals(2, len(list(one2.bs_editable)))
        self.assertEquals(2, len(list(one2.bs_published)))
        self.assertEquals(3, len(list(one2.bs)))
        
        # now we publish the edited relation
        b1_editable = b1_editable.publish()
 
        # we still have 3 related objects, with one archived
        self.assertEquals(3, len(list(one2.bs)))
        self.assertEquals(1, count_archived(one2.bs))
        self.assertEquals(2, count_status(one2.bs, clio.PUBLISHED))

        # in other words...
        self.assertEquals(1, len(list(one2.bs_archived)))
        self.assertEquals(2, len(list(one2.bs_editable)))
        self.assertEquals(2, len(list(one2.bs_published)))

    def test_edit_with_editable_relation(self):
        """We edit an object that already had an editable relation.
        """
        one = self._get_rel_published()
        b = one.bs_published[0]
        b_editable = b.edit()
        b_editable.message = u"B1 edited"

        one_editable = one.edit()
        
        editable_bs = sorted(one_editable.bs_editable, key=lambda o: o.message)
        self.assertEquals(b_editable,
                          editable_bs[0])
        self.assertEquals(u'B1 edited', editable_bs[0].message)
        self.assertEquals(one_editable, editable_bs[0].a)

    def test_many_to_many(self):
        c0 = C(c_code(self.session), u'c0')
        c1 = C(c_code(self.session), u'c1')
        c2 = C(c_code(self.session), u'c2')
        
        self.session.add_all([c0, c1, c2])
        
        d0 = D(d_code(self.session), u'd0')
        d1 = D(d_code(self.session), u'd1')
        d2 = D(d_code(self.session), u'd2')
        self.session.add_all([d0, d1, d2])
        
        c0.ds.append(d0)
        c0.ds.append(d1)

        c1.ds.append(d1)
        c1.ds.append(d2)

        self.session.flush()
        
        # we publish c0, but just c0.
        c0.publish()
        # the ds will still be attached to it, unpublished
        self.assertEquals(2, len(list(c0.ds)))
        self.assertEquals(0, len(list(c0.ds_published)))
        # when we publish d0, we will see one d
        d0.publish()
        self.assertEquals(1, len(list(c0.ds_published)))
        self.assertEquals(d0, c0.ds_published[0])

    def test_many_to_many_edit(self):
        c0 = C(c_code(self.session), u'c0')
        c1 = C(c_code(self.session), u'c1')
        c2 = C(c_code(self.session), u'c2')
        
        self.session.add_all([c0, c1, c2])
        
        d0 = D(d_code(self.session), u'd0')
        d1 = D(d_code(self.session), u'd1')
        d2 = D(d_code(self.session), u'd2')
        self.session.add_all([d0, d1, d2])
        
        c0.ds.append(d0)
        c0.ds.append(d1)

        c1.ds.append(d1)
        c1.ds.append(d2)

        self.session.flush()

        c0.publish()
        d0.publish()

        self.assertEquals(d0, c0.ds_published[0])
        c0_editable = c0.edit()
        self.assertEquals(d0, c0_editable.ds_published[0])
        
    def test_many_to_many_delete(self):
        c0 = C(c_code(self.session), u'c0')
        c1 = C(c_code(self.session), u'c1')
        c2 = C(c_code(self.session), u'c2')
        
        self.session.add_all([c0, c1, c2])
        
        d0 = D(d_code(self.session), u'd0')
        d1 = D(d_code(self.session), u'd1')
        d2 = D(d_code(self.session), u'd2')
        self.session.add_all([d0, d1, d2])
        
        c0.ds.append(d0)
        c0.ds.append(d1)

        c1.ds.append(d1)
        c1.ds.append(d2)

        self.session.flush()

        c0.publish()
        d0.publish()

        self.assertEquals(d0, c0.ds_published[0])
        c0_deletable = c0.delete()
        self.assertEquals(d0, c0_deletable.ds_published[0])
        
    # XXX to be written
    def test_edit_many_to_many(self):
        pass
    
    def test_edit_related_under_edit(self):
        one = self._get_rel_published()
        b1_editable = one.bs[0].edit()

        one_editable = one.edit()
        self.assertEquals(clio.EDITABLE, one_editable.status)
        self.assertEquals(2, len(list(one_editable.bs)))
        self.assertEquals(clio.EDITABLE, one_editable.bs[0].status)
        self.assertEquals(clio.EDITABLE, one_editable.bs[1].status)
    
    def test_compare_all_published(self):
        one = self._get_rel_published()
        
        compared = one.compare_relation('bs')
        self.assertEquals([], compared.deleted)
        self.assertEquals([], compared.edited)
        self.assertEquals(list(one.bs_published),
                          compared.unchanged)

    def test_compare_all_editable(self):
        one = self._get_rel_published()
        one_editable = one.edit()
        
        compared = one_editable.compare_relation('bs')
        self.assertEquals([], compared.deleted)
        self.assertEquals(list(one_editable.bs_editable), compared.edited)
        self.assertEquals([], compared.unchanged)

    def test_compare_relation_editable(self):
        one = self._get_rel_published()

        b1_editable = one.bs[0].edit()
        
        compared = one.compare_relation('bs')
        self.assertEquals([], compared.deleted)
        self.assertEquals([b1_editable], compared.edited)
        self.assertEquals([one.bs[1]], compared.unchanged)

    def test_compare_relation_editable_all_editable(self):
        one = self._get_rel_published()

        b1_editable = one.bs[0].edit()

        one_editable = one.edit()
        
        compared = one_editable.compare_relation('bs')
        self.assertEquals([], compared.deleted)
        self.assertEquals(list(one_editable.bs_editable), compared.edited)
        self.assertEquals([], compared.unchanged)

    def test_compare_relation_deleted(self):
        one = self._get_rel_published()

        b1_deleted = one.bs[0].delete()

        compared = one.compare_relation('bs')

        self.assertEquals([b1_deleted], compared.deleted)
        self.assertEquals([], compared.edited)
        self.assertEquals([one.bs[1]], compared.unchanged)
        

def count_status(l, status):
    result = 0
    for entry in l:
        if entry.status == status:
            result += 1
    return result

def count_archived(l):
    result = 0
    for entry in l:
        if entry.is_archived():
            result += 1
    return result

class CopyModelTestCase(unittest.TestCase):
    def setUp(self):
        engine = create_engine('mysql:///clio_tests')
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.session.query(B).delete()
        self.session.query(A).delete()
        self.session.flush()
        
    def tearDown(self):
        self.session.commit()

    def test_copy_model(self):        
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        self.session.commit()

        new = one._create_edit_copy()
        self.session.add(new)
        self.session.commit()

        self.assertEquals(2, len(self.session.query(A).all()))
        
    def test_copy_model_related_new(self):        
        one = A(a_code(self.session), u'One')
        self.session.add(one)
        
        b1 = B(b_code(self.session), u'B1')
        b2 = B(b_code(self.session), u'B2')
        one.bs.append(b1)
        one.bs.append(b2)

        new = one._create_edit_copy()
        self.session.add(new)
        
        self.assertEquals(2, len(list(new.bs_editable)))

    def test_copy_model_related_published(self):

        one = A(a_code(self.session), u'One')
        self.session.add(one)
       
        b1 = B(b_code(self.session), u'B1')
        b2 = B(b_code(self.session), u'B2')
        one.bs.append(b1)
        one.bs.append(b2)

        one = one.publish()
        
        new = one._create_edit_copy()
        self.session.add(new)
        
        self.assertEquals(2, len(list(new.bs_editable)))

def readmeSetUp(test):
    pass

    
def test_suite():
    optionflags=(doctest.ELLIPSIS+
                 doctest.NORMALIZE_WHITESPACE+
                 doctest.REPORT_NDIFF)
    
    suite = unittest.TestSuite()
    suite.addTests([
            unittest.makeSuite(ClioTestCase),
            unittest.makeSuite(CopyModelTestCase),
            doctest.DocFileSuite('README.txt',
                                 setUp=readmeSetUp,
                                 optionflags=optionflags)
            ])
    return suite
