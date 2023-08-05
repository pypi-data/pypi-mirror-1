import os
import shutil
import tempfile

import _path_cheesecake
from _helper_cheesecake import DATA_PATH, Glutton, create_empty_file
from cheesecake.cheesecake_index import IndexPyLint
from cheesecake import logger


class TestIndexPyLint(object):
    def test_import_self(self):
        files_list = ['import_self.py']
        package_dir = DATA_PATH

        index = IndexPyLint()
        index.cheesecake = Glutton()

        index.compute(files_list, package_dir, 120)

        # Check that package got maximum score, what means importing self
        #     is not decreasing the score.
        print index.value
        assert index.value == index.max_value

    def test_long_file_list(self):
        "Test if pylint index works for long files lists."
        _package_dir = tempfile.mkdtemp()
        _files_list = map(lambda x: 'long_module_with_a_number_%d.py' % x, xrange(4000))

        for filename in _files_list:
            create_empty_file(os.path.join(_package_dir, filename))

        logger.setconsumer('console', logger.STDOUT)
        console_log = logger.MultipleProducer('cheesecake console')

        class CheesecakeMockup(object):
            package_dir = _package_dir
            files_list = _files_list
            log = console_log

        index = IndexPyLint()
        cheesecake = CheesecakeMockup()

        index.compute_with(cheesecake)
        assert index.details != "encountered an error during pylint execution"

        # Clean up.
        shutil.rmtree(_package_dir)
