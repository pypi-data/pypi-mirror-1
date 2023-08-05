import os
import tempfile

import _path_cheesecake
from _helper_cheesecake import DATA_PATH
from cheesecake.cheesecake_index import Cheesecake, CheesecakeError, pad_msg, IndexUrlDownload
        
default_temp_directory = os.path.join(tempfile.gettempdir(), 'cheesecake_sandbox')


class TestIndexInstallability(object):
    def setUp(self):
        self.cheesecake = None

    def _run_it(self, test_fun):
        logfile = tempfile.mktemp()

        try:
            test_fun(logfile)
        finally:
            if self.cheesecake:
                self.cheesecake.cleanup()

            if os.path.exists(logfile):
                os.unlink(logfile)

    def test_index_url_download_valid_url(self):
        urls = [
            "http://www.agilistas.org/cheesecake/nose-0.8.3.tar.gz",
            "file://%s" % os.path.join(DATA_PATH, "nose-0.8.3.tar.gz")
        ]

        for url in urls:
            def test_fun(logfile):
                try:
                    self.cheesecake = Cheesecake(url=url, logfile=logfile)

                    index = self.cheesecake.index["INSTALLABILITY"]["IndexUrlDownload"]
                    index.compute_with(self.cheesecake)

                    assert index.name == "IndexUrlDownload"
                    assert index.value == IndexUrlDownload.max_value
                    assert index.details == "downloaded package " + \
                           self.cheesecake.package + " from URL " + \
                           self.cheesecake.url
                except CheesecakeError, e:
                    # it's OK if we get "connection refused" sometimes
                    msg = "[Errno socket error] (111, 'Connection refused')\n"
                    msg += "Detailed info available in log file %s" % logfile
                    assert str(e) == msg

            self._run_it(test_fun)

    def test_index_url_download_invalid_url(self):
        def test_fun(logfile):
            try:
                self.cheesecake = Cheesecake(url="http://www.agilistas.org/cheesecake/not_there.tar.gz",
                                             sandbox=default_temp_directory, logfile=logfile)
                assert 0 # This statement should not be reached
            except CheesecakeError, e:
                msg = "Got '404 Not Found' error while trying to download package ... exiting"
                msg += "\nDetailed info available in log file %s" % logfile
                assert str(e) == msg

        self._run_it(test_fun)
