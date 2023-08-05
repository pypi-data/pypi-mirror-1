import os
import tempfile
from releasemanager import utils

class MockResource(object):
    def __init__(self, name):
        orig_dir = os.getcwd()
        tmpdir = tempfile.mkdtemp(prefix="rlsmgr_")
        fake_data = "test data"
        for num in range(0, 10):
            fname = tempfile.mktemp(dir=tmpdir)
            fh = open(fname, 'w')
            fh.write("%s: %s" % (fake_data, num))
            fh.close()
        utils.makeZip(tmpdir, tmpdir, "%s.zip" % name)
        self.data = open(os.path.join(tmpdir, "%s.zip" % name)).read()
        utils.clean(tempfile.gettempdir(), os.path.split(tmpdir)[1], work_dir=orig_dir, ignoreErrors=True)