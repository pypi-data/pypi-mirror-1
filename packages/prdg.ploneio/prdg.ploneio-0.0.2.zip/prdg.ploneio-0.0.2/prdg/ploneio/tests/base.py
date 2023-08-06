"""Setup the environment for tests."""
from Products.PloneTestCase import PloneTestCase as ptc

from prdg.plone.testing import IntegrationTestCase, FunctionalTestCase
from prdg.util.file import exists

from StringIO import StringIO

import tarfile
import tempfile
import os.path
from shutil import rmtree

class BaseTestCase(IntegrationTestCase, FunctionalTestCase):
    def afterSetUp(self):
        IntegrationTestCase.afterSetUp(self)
        FunctionalTestCase.afterSetUp(self)
        self.tmpdir = os.path.join(tempfile.gettempdir(), 'ploneiotest')
        self.catalog = self.portal.portal_catalog
        
    def extract_to_str(self, tar_gz_str, filename_to_extract):
        f = StringIO(tar_gz_str)
        tar = tarfile.open(name='', mode='r:gz', fileobj=f)
        extracted = tar.extractfile(filename_to_extract)
        return extracted.read()
    
    def beforeTearDown(self):
        if exists(self.tmpdir):
            rmtree(self.tmpdir)

ptc.setupPloneSite()
