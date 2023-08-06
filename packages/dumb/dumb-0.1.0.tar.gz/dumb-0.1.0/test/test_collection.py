#!/usr/bin/env python

import tempfile,os
import dumb
import unittest

class TestCollection(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.cl = dumb.Collection(self.directory)

    def tearDown(self):
        os.rmdir(self.directory)

    def testAddBMWithTag(self):
        self.cl.add_bookmark('http://www.example.org',{'tag':['prova']})
        self.assertEqual(self.cl.get_tags(),['prova'])

    def testAddMBWoutTag(self):
        self.cl.add_bookmark('http://www.example.org')
        self.assertEqual(self.cl.get_tags(),[])

    def testPlainGetBookmarks(self):
        urls = ['http://www.example.org','http//www.example.com']
        for url in urls:
            self.cl.add_bookmark(url)
        for bm in self.cl.get_bookmarks():
            self.assertTrue(bm.get_value('url') in urls)
            urls.remove(bm.get_value('url'))

    def testGetBookmarksByTag(self):
        urls = ['http://www.example.org','http://www.example.it']
        self.cl.add_bookmark('http://www.example.org',{'tag':['prova','test']})
        self.cl.add_bookmark('http://www.example.it',{'tag':['prova']})
        self.cl.add_bookmark('http://www.example.com')
        for bm in self.cl.get_bookmarks(['prova']):
            self.assertTrue(bm.get_value('url') in urls)
            urls.remove(bm.get_value('url'))


class TestCollectionFiles(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.cl = dumb.Collection(self.directory)

    def tearDown(self):
        # TODO: remove all of the files in the directory
        os.rmdir(self.directory)

    def testLoadCollectionWithTags(self):
        bm = dumb.Bookmark(None,self.directory,'http://www.example.com')
        bm.save
        bm = dumb.Bookmark(None,self.directory,'http://www.example.org')
        bm.save
        self.cl.load()
        urls = ['http://www.example.org','http//www.example.com']
        for bm in self.cl.get_bookmarks():
            self.assertTrue(bm.get_value('url') in urls)
            urls.remove(bm.get_value('url'))

    def testLoadCollectionWoutTags(self):
        bm = dumb.Bookmark(None,self.directory,'http://www.example.com')
        bm.set_value('tag',['prova'])
        bm.save
        bm = dumb.Bookmark(None,self.directory,'http://www.example.org')
        bm.save
        self.cl.load()
        urls = ['http://www.example.org','http//www.example.com']
        for bm in self.cl.get_bookmarks():
            self.assertTrue(bm.get_value('url') in urls)
            urls.remove(bm.get_value('url'))
        urls = ['http//www.example.com']
        for bm in self.cl.get_bookmarks(['prova']):
            self.assertTrue(bm.get_value('url') in urls)
            urls.remove(bm.get_value('url'))


if __name__ == '__main__':
        unittest.main()
