import os

import _path_cheesecake
from _helper_cheesecake import DATA_PATH

from cheesecake.cheesecake_index import Cheesecake
from cheesecake.cheesecake_index import IndexPyPIDownload
from cheesecake.cheesecake_index import IndexUnpack
from cheesecake.cheesecake_index import IndexUnpackDir
from cheesecake.cheesecake_index import IndexSetupPy
from cheesecake.cheesecake_index import IndexInstall
from cheesecake.cheesecake_index import IndexUrlDownload
from cheesecake.cheesecake_index import IndexGeneratedFiles


class TestIndexInstallability(object):
    def setUp(self):
        self.cheesecake = None

    def tearDown(self):
        if not self.cheesecake:
            return
        self.cheesecake.cleanup()

    def test_index_installability_local_path(self):
        self.cheesecake = Cheesecake(path=os.path.join(DATA_PATH, "nose-0.8.3.tar.gz"))

        index = self.cheesecake.index["INSTALLABILITY"]
        parts = [IndexUnpack, IndexUnpackDir, IndexSetupPy, IndexInstall, IndexGeneratedFiles]

        assert index.max_value == sum(map(lambda x: x.max_value, parts))

        index.compute_with(self.cheesecake)
        assert index.value == sum(map(lambda x: x.max_value, parts))

    def test_index_installability_url_download(self):
        self.cheesecake = Cheesecake(url="http://www.agilistas.org/cheesecake/nose-0.8.3.tar.gz")

        index = self.cheesecake.index["INSTALLABILITY"]
        parts = [IndexUrlDownload, IndexUnpack, IndexUnpackDir, IndexSetupPy, IndexInstall, IndexGeneratedFiles]

        assert index.max_value == sum(map(lambda x: x.max_value, parts))

        index.compute_with(self.cheesecake)
        assert index.value == sum(map(lambda x: x.max_value, parts))
