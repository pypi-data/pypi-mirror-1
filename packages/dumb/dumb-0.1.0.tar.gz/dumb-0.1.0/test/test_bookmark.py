#!/usr/bin/env python

import dumb
import unittest
import tempfile, os

class TestBookmark(unittest.TestCase):

    def setUp(self):
        self.bm = dumb.Bookmark(None,'/tmp',url="http://example.com")
        pass

    def tearDown(self):
        pass

    def testsetplainvalue(self):
        self.bm.set_value('title','Example website')
        self.assertEqual(self.bm.get_value('title'),'Example website')

    def testsetmultivalue(self):
        self.bm.set_value('tag',['example','test'])
        self.assertEqual(self.bm.get_value('tag'),['example','test'])

    def testsetwrongtag(self):
        self.assertRaises(ValueError,self.bm.set_value,'foobar','foo')

    def testsetwrongvalue(self):
        self.assertRaises(ValueError,self.bm.set_value,'tag','sample')

    def testgetparsedvalue(self):
        self.bm.set_value('cline','links %(url)s')
        self.assertEqual(self.bm.get_parsed_value('cline'),'links http://example.com')

    def testgetparsedplainvalue(self):
        self.bm.set_value('title','Example website')
        self.assertEqual(self.bm.get_parsed_value('title'),'Example website')

    def testgetwrongparsedvalue(self):
        if not self.bm.has_key('cline'):
            self.assertRaises(KeyError,self.bm.get_parsed_value,'cline')


class TestBookmarkFiles(unittest.TestCase):

    def setUp(self):
        # safer version: requires python 2.6+
        #fp = tempfile.NamedTemporaryFile(delete=False)
        #self.filename = fp.name
        #fp.close()
        self.filename = tempfile.mktemp()
        pass

    def tearDown(self):
        os.unlink(self.filename)

    def testbookmarksave(self):
        bm = dumb.Bookmark(os.path.basename(self.filename),os.path.dirname(self.filename))
        bm.set_value('url','http://www.example.com')
        bm.set_value('tag',['sample','test'])
        bm.set_value('title','Example')
        bm.save()
        fp = file(self.filename)
        lines = fp.readlines()
        fp.close()
        self.assertTrue('url: http://www.example.com\n' in lines)
        self.assertTrue('tag: sample; test\n' in lines)
        self.assertTrue('title: Example\n' in lines)

    def testbookmarkload(self):
        fp = file(self.filename,'w')
        fp.write('url: http://www.example.com\n')
        fp.write('tag: sample; test\n')
        fp.write('title: Example\n')
        fp.write('cline: links %(url)s\n')
        fp.write('opener: browser; editor\n')
        fp.write('comment: An example website\n')
        fp.close()
        bm = dumb.Bookmark(os.path.basename(self.filename),os.path.dirname(self.filename))
        bm.load()
        self.assertEqual(bm.get_value('url'),'http://www.example.com')
        self.assertEqual(bm.get_value('title'),'Example')
        self.assertEqual(bm.get_value('cline'),'links %(url)s')
        self.assertEqual(bm.get_value('comment'),'An example website')
        self.assertEqual(bm.get_value('tag'),['sample','test'])
        self.assertEqual(bm.get_value('opener'),['browser','editor'])

    # TODO: add tests for error conditions


if __name__ == '__main__':
        unittest.main()
