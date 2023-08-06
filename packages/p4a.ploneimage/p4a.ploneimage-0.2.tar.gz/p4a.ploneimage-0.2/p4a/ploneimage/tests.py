import os
import unittest
import doctest
from zope.testing import doctestunit

from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite
from App import Common
from Products.PloneTestCase import layer
from Products.PloneTestCase import ptc

import p4a.image.tests # for Common.pkg_home
p4a.image.tests # pyflakes

from p4a import ploneimage
from p4a.ploneimage import testing

def test_suite():
    suite = unittest.TestSuite()
    if __name__ not in ('__main__', 'p4a.ploneimage.tests'):
        return suite
    
    suite.addTest(doctestunit.DocTestSuite('p4a.ploneimage.atct'))
    
    if ploneimage.has_ATPhoto_support():
        from p4a.ploneimage.ATPhoto import ATPhototests
        suite.addTest(ATPhototests.test_suite())

    if ploneimage.has_fatsyndication_support():
        suite.addTest(ZopeDocFileSuite(
            'syndication.txt',
            package='p4a.ploneimage',
            test_class=testing.IntegrationTestCase,
            optionflags=doctest.ELLIPSIS,
            )
        )

    suite.addTest(ZopeDocFileSuite(
        'plone-image.txt',
        package='p4a.ploneimage',
        test_class=testing.testclass_builder(image_type='Image')
        )
    )

    install_suite = FunctionalDocFileSuite(
        'install.txt',
        'browser.txt',
        test_class=ptc.PloneTestCase)
    install_suite.layer = testing.install_layer
    suite.addTest(install_suite)
    
    pkg_home = Common.package_home({'__name__': 'p4a.image.tests'})
    samplesdir = os.path.join(pkg_home, 'samples')
    
    fields = {'title': u'U.S.S. Constitution',
              'photographer': u'Eric Coffman',
              'action advised': None,
              'by-line title': u"Eric Coffman's Title",
              'category': u'Art',
              'city': u'Boston',
              'contact': [],
              'content location code': None,
              'content location name': None,
              'copyright': u'Eric Coffman',
              'country': u'USA',
              'credit': u'BRC',
              'custom1': None,
              'custom10': None,
              'custom11': None,
              'custom12': None,
              'custom13': None,
              'custom14': None,
              'custom15': None,
              'custom16': None,
              'custom17': None,
              'custom18': None,
              'custom19': None,
              'custom2': None,
              'custom20': None,
              'custom3': None,
              'custom4': None,
              'custom5': None,
              'custom6': None,
              'custom7': None,
              'custom8': None,
              'custom9': None,
              'date created': u'20080606',
              'description': u'Oldest still commissioned ship in the US fleet.',
              'digital creation date': None,
              'digital creation time': None,
              'edit status': None,
              'editorial update': None,
              'expiration date': None,
              'expiration time': None,
              'fixture identifier': None,
              'headline': u'USS Constitution gets new sails.',
              'image orientation': None,
              'image type': None,
              'isoCountryCode': u'USA',
              'keywords': [u'Boat', u'Mast', u'Crane', u'House'],
              'language identifier': None,
              'location': None,
              'object cycle': None,
              'original transmission reference': u'BRC',
              'originating program': None,
              'program version': None,
              'reference date': None,
              'reference number': None,
              'reference service': None,
              'release date': None,
              'release time': None,
              'source': u'Eric Coffman',
              'special instructions': u'Contact before use.',
              'state': u'MA',
              'subject reference': None,
              'supplemental category': [u'Historical', u'Manufacturing'],
              'time created': None,
              'urgency': None,
              'writer/editor': u'George Jetson'}
    SAMPLES = ((os.path.join(samplesdir, 'USS_Constitution.jpg'),
                'image/jpeg', fields),)

    for sampleimage, mimetype, fields in SAMPLES:
        suite.addTest(ZopeDocFileSuite(
            'plone-image-impl.txt',
            package='p4a.ploneimage',
            test_class=testing.testclass_builder(sampleimage=sampleimage,
                                                 required_mimetype=mimetype,
                                                 image_content_type='Image',
                                                 fields=fields)
            )
        )

    if ploneimage.has_blobfile_support():
        # setup the same test to run against BlobFile if available
        sampleimage, mimetype, fields = SAMPLES[0]
        suite.addTest(ZopeDocFileSuite(
            'plone-image-impl.txt',
            package='p4a.ploneimage',
            test_class=testing.testclass_builder(sampleimage=sampleimage,
                                                 required_mimetype=mimetype,
                                                 image_content_type='BlobImage',
                                                 fields=fields)
            )
        )

    suite.layer = layer.ZCMLLayer

    return suite
