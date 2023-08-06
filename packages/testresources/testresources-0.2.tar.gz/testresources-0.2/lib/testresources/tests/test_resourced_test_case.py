#
#  testresources: extensions to python unittest to allow declaritive use
#  of resources by test cases.
#  Copyright (C) 2005  Robert Collins <robertc@robertcollins.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import testtools
import testresources
from testresources.tests import ResultWithResourceExtensions


def test_suite():
    loader = testresources.tests.TestUtil.TestLoader()
    result = loader.loadTestsFromName(__name__)
    return result


class MockResource(testresources.TestResource):
    """Resource used for testing ResourcedTestCase."""

    def __init__(self, resource):
        testresources.TestResource.__init__(self)
        self._resource = resource

    def make(self, dependency_resources):
        return self._resource


class MockResourceInstance(object):
    """A resource instance."""


class TestResourcedTestCase(testtools.TestCase):

    def setUp(self):
        testtools.TestCase.setUp(self)
        class Example(testresources.ResourcedTestCase):
            def test_example(self):
                pass
        self.resourced_case = Example('test_example')
        self.resource = self.getUniqueString()
        self.resource_manager = MockResource(self.resource)

    def testDefaults(self):
        self.assertEqual(self.resourced_case.resources, [])

    def testResultPassedToResources(self):
        result = ResultWithResourceExtensions()
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.run(result)
        self.assertEqual(4, len(result._calls))

    def testSetUpResourcesSingle(self):
        # setUpResources installs the resources listed in ResourcedTestCase.
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.setUpResources()
        self.assertEqual(self.resource, self.resourced_case.foo)

    def testSetUpResourcesMultiple(self):
        # setUpResources installs the resources listed in ResourcedTestCase.
        self.resourced_case.resources = [
            ('foo', self.resource_manager),
            ('bar', MockResource('bar_resource'))]
        self.resourced_case.setUpResources()
        self.assertEqual(self.resource, self.resourced_case.foo)
        self.assertEqual('bar_resource', self.resourced_case.bar)

    def testSetUpResourcesSetsUpDependences(self):
        resource = MockResourceInstance()
        self.resource_manager = MockResource(resource)
        self.resourced_case.resources = [('foo', self.resource_manager)]
        # Give the 'foo' resource access to a 'bar' resource
        self.resource_manager.resources.append(
            ('bar', MockResource('bar_resource')))
        self.resourced_case.setUpResources()
        self.assertEqual(resource, self.resourced_case.foo)
        self.assertEqual('bar_resource', self.resourced_case.foo.bar)

    def testSetUpUsesResource(self):
        # setUpResources records a use of each declared resource.
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.setUpResources()
        self.assertEqual(self.resource_manager._uses, 1)

    def testTearDownResourcesDeletesResourceAttributes(self):
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.setUpResources()
        self.resourced_case.tearDownResources()
        self.failIf(hasattr(self.resourced_case, "foo"))

    def testTearDownResourcesStopsUsingResource(self):
        # tearDownResources records that there is one less use of each
        # declared resource.
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.setUpResources()
        self.resourced_case.tearDownResources()
        self.assertEqual(self.resource_manager._uses, 0)

    def testTearDownResourcesStopsUsingDependencies(self):
        resource = MockResourceInstance()
        dep1 = MockResource('bar_resource')
        self.resource_manager = MockResource(resource)
        self.resourced_case.resources = [('foo', self.resource_manager)]
        # Give the 'foo' resource access to a 'bar' resource
        self.resource_manager.resources.append(
            ('bar', dep1))
        self.resourced_case.setUpResources()
        self.resourced_case.tearDownResources()
        self.assertEqual(dep1._uses, 0)

    def testSingleWithSetup(self):
        # setUp and tearDown invoke setUpResources and tearDownResources.
        self.resourced_case.resources = [("foo", self.resource_manager)]
        self.resourced_case.setUp()
        self.assertEqual(self.resourced_case.foo, self.resource)
        self.assertEqual(self.resource_manager._uses, 1)
        self.resourced_case.tearDown()
        self.failIf(hasattr(self.resourced_case, "foo"))
        self.assertEqual(self.resource_manager._uses, 0)
