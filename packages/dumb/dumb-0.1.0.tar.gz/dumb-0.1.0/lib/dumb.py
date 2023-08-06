#!/usr/bin/env python

""" 
pydumb

pydumb is a Python module to manage a dumb collection of bookmarks

"""

__author__ = 'Elena "of Valhalla" Grandi'
__version__ = '20090521'
__copyright__ = '2009 Elena Grandi'
__license__ = 'LGPL'

import os
import md5

SINGLE_VALUED=['url','title','cline','comment']
MULTI_VALUED=['opener','tag']

class Collection:
    """"""

    def __init__(self,directory):
        """"""
        self.directory = directory
        self.bookmarks = {}
        self.tags = []

    def load(self):
        """Reads the bookmarks in the collection directory"""
        for bfile in os.listdir(self.directory):
            try:
                bm = Bookmark(os.path.basename(bfile),self.directory)
                loaded = bm.load()
            # FIXME: fix the exception management
            except IOError:
                print "uh oh"
            if loaded:
                self.bookmarks[bm.get_value('url')] = bm
                for tag in bm.get_value('tag'):
                    if tag not in self.tags:
                        self.tags.append(tag)

    def save(self):
        """Saves the current bookmarks"""
        for bm in self.bookmarks:
            self.bookmarks[bm].save()

    def add_bookmark(self,url,data={}):
        """Adds a new bookmark to the collection and sets a dict of data"""
        self.bookmarks[url] = Bookmark(None,self.directory,url=url)
        for item in data:
            self.bookmarks[url].set_value(item,data[item])
            if item == 'tag':
                for tag in data[item]:
                    if tag not in self.tags:
                        self.tags.append(tag)

    def get_bookmarks(self,tags=None):
        """Returns a list of the bookmarks with the given tags.
        If tags == None, return every bookmark in the collection."""
        if tags == None:
            return self.bookmarks.values()
        bms = []
        if type(tags) == list:
            for bm in self.bookmarks:
                for tag in tags:
                    if self.bookmarks[bm].has_key('tag') and tag in self.bookmarks[bm].get_value('tag'):
                        bms.append(self.bookmarks[bm])
                        break
        return bms

    def get_bookmark(self,url):
        """Returns the bookmark with the given hash"""
        return self.bookmarks[url]

    def get_tags(self):
        return self.tags


class Bookmark:
    """"""

    def __init__(self,hash,directory,url=None):
        """Creates a new bookmark instance.
        If a filename is given (as a string) it is used for future 
        operations; otherwise and if an url is given the filename 
        is generated as an hash of the url."""
        self.data = {}
        if type(hash) != str:
            if type(url) == str:
                self.data['url'] = url
                hash = md5.md5(url).hexdigest()
            else:
                raise ValueError, "a Bookmark must be initialized with either a filename or an url"
        self.filename=os.path.join(directory,hash)

    def __str__(self):
        return self.filename + "\n" + str(self.data)

    def has_key(self,key):
        """Returns whether this bookmark has the given key"""
        return self.data.has_key(key)

    def get_value(self,key):
        """Returns the value of the given key"""
        return self.data[key]

    def get_values(self):
        """Returns the full dict with the values of this bookmark"""
        return self.data

    def get_parsed_value(self,key):
        """Returns the value of the given key with %(url)s explicited"""
        return self.data[key].replace("%(url)s",self.data['url'])

    def set_value(self,key,value):
        """Sets the value for the given key"""
        if (key in SINGLE_VALUED and type(value) == str) or (
                key in MULTI_VALUED and type(value) == list):
            self.data[key] = value
        else:
            raise ValueError, "invalid key,value for a Bookmark"

    def load(self,filename=None):
        """Loads the bookmark from a file"""
        if filename == None:
            filename = self.filename
        try:
            fp = open(filename,'r')
        except IOError:
            print "Could not open"+filename
            return False
        for line in fp.readlines():
            item = line.split(':',1)
            # ignore lines that don't look like key: value
            if len(item) == 2:
                item[1] = item[1].strip()
                # recognise data with single values
                if item[0] in SINGLE_VALUED:
                    self.data[item[0]] = item[1]
                # recognise data with multiple values
                elif item[0] in MULTI_VALUED:
                    self.data[item[0]] = [ vl.strip() for vl in item[1].split(';')]
        fp.close()
        return True

    def save(self,filename=None):
        """Saves the bookmark to file; overvrites existing data"""
        if filename == None:
            filename = self.filename
        try: 
            fp = open(filename,'w')
        except IOError:
            print "Could not open file",filename
            raise
        try: 
            for item in self.data:
                if type(self.data[item]) == list:
                    line = item+": "
                    for value in self.data[item]:
                        line += value+"; "
                    line = line[:-2]
                    fp.write(line+'\n')
                else:
                    fp.write(item+": "+self.data[item]+'\n')
        except IOError:
            print "Could not write to",filename
            raise
        finally:
            # TODO: check that the file is closed
            fp.close()


def main():
    pass


if __name__ == '__main__': main()
