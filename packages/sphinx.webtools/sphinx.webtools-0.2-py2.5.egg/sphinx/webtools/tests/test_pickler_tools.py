# python import
import unittest

# python import
import os, shutil

# genshi import for xml reformat
from genshi import XML
from genshi.core import Stream

# tools import
from sphinx.webtools.pickler_tools import get_pickler
from sphinx.webtools import get_genentries, get_modentries, \
                        PicklerContentManager, reformat_content_links, \
                        update_docs

class TestPicklerTools(unittest.TestCase):
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

    def test_update_docs(self):
        """
        """
        error = update_docs(self.__source_dir, self.__doc_dir)
        assert not error, 'unexpexted error: %s' % error

        error = update_docs('test_src_dir', self.__doc_dir)
        assert type(error) == Stream, 'unexpexted type: %s' % type(error)

        error = update_docs(None, self.__doc_dir)
        assert type(error) == Stream, 'unexpexted type: %s' % type(error)

        error = update_docs(self.__source_dir, None)
        assert type(error) == Stream, 'unexpexted type: %s' % type(error)

    def test_get_pickler(self):
        """
        """
        # search index test
        pickler_ = get_pickler(
                                    self.__doc_dir, 'searchindex.pickle')
        assert type(pickler_) == dict, 'unexpected type: %s' % type(pickler_)
        filenames = pickler_['filenames']
        titles = pickler_['titles']
        assert type(filenames) == list, 'unexpected type: %s' % type(filenames)
        assert type(titles) == list, 'unexpected type: %s' % type(titles)
        assert len(filenames) == len(titles), 'wrong length: %s != %s' % (
                                                len(filenames), len(titles))
        # index test
        pickler_ = get_pickler(
                                    self.__doc_dir, 'genindex.fpickle')
        assert type(pickler_) == dict, 'unexpected type: %s' % type(pickler_)
        entries = pickler_['genindexentries']
        assert type(entries) == list, 'unexpected type: %s' % type(entries)
        en_dict = entries[0]
        assert type(en_dict) == tuple, 'unexpected type: %s' % type(tuple)
        # content test
        pickler_ = get_pickler(self.__doc_dir, 'content/test1.fpickle')
        assert type(pickler_) == dict, 'unexpected type: %s' % type(pickler_)
        # body content test
        body = XML('<div>%s</div>' % pickler_['body'])
        assert type(body) == Stream, 'unexpected type: %s' % type(body)
        # toc content test
        toc = XML('<div>%s</div>' % pickler_['toc'])
        assert type(toc) == Stream, 'unexpected type: %s' % type(toc)
        # rellinks content test
        rellinks = pickler_['rellinks']
        assert type(rellinks) == list, 'unexpected type: %s' % type(rellinks)
        link_def = rellinks[0]
        assert type(link_def) == tuple, 'unexpected type: %s' % type(link_def)

    def test_reformat_content(self):
        """
        """
        # original XML content
        source_html = """
        <div><a class="reference" href="../test2/#ref">test</a></div>
        """
        source_xml = XML(source_html)
        result_xml = reformat_content_links(
                        self.__base_url, self.__doc_dir, source_xml)
        # check XMl validity
        assert type(result_xml) == Stream, 'unexpected type: %s' % type(
                                                                    result_xml)
        # check function result
        href_result = '%s' % result_xml.select('a').select('@href')
        href_test = 'base_url?action=view&amp;item=content/test2#ref'
        assert href_result == href_test, 'wrong href result: %s' % href_result

        # original XML content
        source_html = """
        <div><a class="reference" href="http://www.test.org">test</a></div>
        """
        source_xml = XML(source_html)
        result_xml = reformat_content_links(
                        self.__base_url, self.__doc_dir, source_xml)
        # check XMl validity
        assert type(result_xml) == Stream, 'unexpected type: %s' % type(
                                                                    result_xml)
        # check function result
        href_result = '%s' % result_xml.select('a').select('@href')
        href_test = 'http://www.test.org'
        assert href_result == href_test, 'wrong href result: %s' % href_result

    def test_pickler_content_manager(self):
        """
        """
        # set content manager
        pickler_ct_manager = PicklerContentManager(
                                self.__base_url, self.__doc_dir, 'index')
        # get rellinks
        rellinks = pickler_ct_manager.get_rellinks()
        link = rellinks[0]
        assert type(rellinks) == list, 'unexpected type: %s' % type(rellinks)
        assert type(link) == dict, 'unexpected type: %s' % type(link)
        # get toc
        toc = XML(pickler_ct_manager.get_toc())
        assert type(toc) == Stream, 'unexpected type: %s' % type(toc)
        # get content
        body = XML(pickler_ct_manager.get_body())
        assert type(body) == Stream, 'unexpected type: %s' % type(body)
        # set content manager
        pickler_ct_manager = PicklerContentManager(
                                self.__base_url, self.__doc_dir, 'bad_name')
        # get rellinks
        rellinks = pickler_ct_manager.get_rellinks()
        assert not rellinks, 'unexpected result: %s' % rellinks
        # get toc
        toc = pickler_ct_manager.get_toc()
        assert not toc, 'unexpected result: %s' % toc
        # get content
        body = pickler_ct_manager.get_body()
        assert not body, 'unexpected result: %s' % body

    def test_get_genentries(self):
        """
        """
        entries = get_genentries(self.__base_url, self.__doc_dir)
        entry = entries[0]
        assert type(entries) == list, 'unexpected result: %s' % type(entries)
        assert type(entry) == dict, 'unexpected result: %s' % type(entry)

    def test_get_modentries(self):
        """
        """
        entries = get_modentries(self.__base_url, self.__doc_dir)
        entry = entries[0]
        assert type(entries) == list, 'unexpected result: %s' % type(entries)
        assert type(entry) == dict, 'unexpected result: %s' % type(entry)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPicklerTools, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
