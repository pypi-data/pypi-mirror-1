# python import
import unittest

# python import
import os, shutil

# genshi import for xml reformat
from genshi import XML
from genshi.core import Stream

# tools import
from sphinx.webtools import update_docs, PicklerContentManager
# search import
from sphinx.webtools import highlight, search
from sphinx.webtools.search_tools import search_in_file, do_search

class TestSearchTools(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        # current dir
        test_dir = os.path.dirname(__file__)
        # set the source dir of the test documentation
        self.__source_dir = os.path.join(test_dir, 'data')
        # set a doc dir
        self.__doc_dir = os.path.join(test_dir, 'web')
        # set a base url
        self.__base_url = 'base_url'
        # doc update
        update_docs(self.__source_dir, self.__doc_dir)

    def tearDown(self):
        """
        """
        shutil.rmtree(self.__doc_dir)

    def test_highlight(self):
        """
        """
        # set content manager
        pickler_ct_manager = PicklerContentManager(
                                self.__base_url, self.__doc_dir, 'content/test1')
        # get content
        content = pickler_ct_manager.get_body()
        # highlight search
        result = highlight(content, 'test')
        # check result
        assert XML(result), 'cannot reformat highlighted result!'
        assert result.count('class="find"') > 0, 'no highlighted tag!'
        # bad search
        result = highlight(content, None)
        # check result
        assert content == result, 'result should be equal to content'
        # bad search
        result = highlight(content, 'bad_search')
        # check result
        assert result.count('class="find"') == 0, 'invalid result'

    def test_search_in_file(self):
        """
        """
        # variables init
        file = 'content/test1'
        title = 'test1'
        words = 'test'
        result = dict()
        # trigger the search
        search_in_file(self.__doc_dir, file, title, words, result)
        # check result
        assert len(result) > 0, 'no result found!'
        assert result.has_key('content/test1'), 'invalid result!'
        assert type(result['content/test1']) == dict, \
                    'invalid result content: %s' % result
        # check dict
        result_test = result['content/test1']
        assert type(result_test) == dict, 'invalid result content!'
        # check key title
        assert result_test.has_key('title'), \
                    'invalid result content: %s' % result_test
        assert result_test['title'] == 'test1', \
                    'invalid result content title: %s' % result_test['title']
        # check key lines
        lines = result_test['lines']
        assert type(lines) == list, 'invalid result content!'
        assert len(lines) > 0, 'no result found!'

    def test_do_search(self):
        """
        """
        # variables init
        words = 'test'
        # trigger the search
        result = do_search(self.__doc_dir, words)
        # check result
        assert type(result) == dict, 'unexpected type: %s' % type(result)
        assert len(result) > 0, 'no result found!'
        assert result.has_key('content/test1'), 'invalid result!'
        assert type(result['content/test1']) == dict, \
                    'invalid result content: %s' % result
        # check dict
        result_test = result['content/test1']
        assert type(result_test) == dict, 'invalid result content!'
        # check key title
        assert result_test.has_key('title'), \
                    'invalid result content: %s' % result_test
        assert result_test['title'] == 'test1', \
                    'invalid result content title: %s' % result_test['title']
        # check key lines
        lines = result_test['lines']
        assert type(lines) == list, 'invalid result content!'
        assert len(lines) > 0, 'no result found!'

    def test_search(self):
        """
        """
        # variables init
        words = 'test'
        # trigger the search
        result = search(self.__base_url, self.__doc_dir, words)
        # check result
        assert type(result) == list, 'unexpected type: %s' % type(result)
        assert len(result) > 0, 'no result found: %s' % len(result)
        # check result item
        item = result[0]
        assert type(item) == dict, 'unexpected type: %s' % type(item)
        # trigger bad search
        result = search(self.__base_url, self.__doc_dir, 'bad_search')
        assert not result, 'invalid result: %s' % result

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSearchTools, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
