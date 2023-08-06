import unittest

import zope.testing.module

# these are used by setup
import transaction
from ZODB.interfaces import IConnection
from ZODB.tests.util import DB

from persistent.interfaces import IPersistent

from zope import component
import zope.component.interfaces
import zope.location.interfaces
import zope.annotation
from zope.app.testing import placelesssetup
from zope.app.keyreference.persistent import KeyReferenceToPersistent, connectionOfPersistent
from zope.app.folder import rootFolder
from zope.app.component.site import LocalSiteManager, SiteManagerAdapter
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
import zope.app.component.hooks

from testing import FunctionalDocFileSuite, FunctionalLayer

import bebop.ordering.interfaces

from largeblue.pages.order import ordering, orderable
from largeblue.pages.interfaces import IPage, IPageContainer
from largeblue.pages.page import pageFactory, fileFactory
from largeblue.pages import subscribers

__docformat__ = "reStructuredText"


def setup(test):
    placelesssetup.setUp()
    component.provideAdapter(
        KeyReferenceToPersistent, 
        adapts = (
            IPersistent,
        )
    )
    component.provideAdapter(
        SiteManagerAdapter, (
            zope.location.interfaces.ILocation,
        ),
        zope.component.interfaces.IComponentLookup
    )
    component.provideAdapter(
        connectionOfPersistent,
        adapts = (
            IPersistent,
        ),
        provides = IConnection
    )
    component.provideAdapter(
        factory = zope.annotation.attribute.AttributeAnnotations,
        adapts = (
            zope.annotation.interfaces.IAttributeAnnotatable,
        ),
        provides = zope.annotation.interfaces.IAnnotations
    )
    component.provideAdapter(
        factory = ordering.Ordering,
        adapts = (
            IPageContainer,
        )
    )
    component.provideAdapter(
        factory = ordering.Ordering,
        adapts = (
            IPageContainer,
        )
    )
    component.provideAdapter(
        factory = orderable.OrderableFactory
    )
    component.provideHandler(subscribers.handle_created)
    component.provideHandler(subscribers.handle_modified)
    component.provideHandler(subscribers.handle_added)
    component.provideHandler(subscribers.handle_deleted)
    component.provideHandler(subscribers.handle_reindex)
    test.globs['db'] = db = DB()
    test.globs['conn'] = conn = db.open()
    test.globs['root'] = root = conn.root()
    test.globs['app'] = app = root['app'] = rootFolder()
    app.setSiteManager(
        LocalSiteManager(app)
    )
    zope.app.component.hooks.setSite(app)
    zope.app.component.hooks.setHooks()
    sm = app.getSiteManager()
    sm['intids'] = IntIds()
    registry = zope.component.interfaces.IComponentRegistry(sm)
    registry.registerUtility(sm['intids'], IIntIds)
    registry.registerUtility(
        pageFactory,
        zope.component.interfaces.IFactory, 
        'largeblue.pages.Page'
    )
    registry.registerUtility(
        fileFactory,
        zope.component.interfaces.IFactory, 
        'largeblue.pages.File'
    )
    transaction.commit()

def tearDown(test):
    zope.app.component.hooks.resetHooks()
    zope.app.component.hooks.setSite()
    transaction.abort()
    test.globs['db'].close()
    placelesssetup.tearDown()


def READMESetUp(test):
    setup(test)
    zope.testing.module.setUp(
        test, 
        'largeblue.pages.README'
    )

def READMETearDown(test):
    tearDown(test)
    zope.testing.module.tearDown(test)


def test_suite():
    return FunctionalDocFileSuite(
        'README.txt',
        setUp = READMESetUp, 
        tearDown = READMETearDown
    )


if __name__ == '__main__':
    unittest.main(
        defaultTest = 'test_suite'
    )