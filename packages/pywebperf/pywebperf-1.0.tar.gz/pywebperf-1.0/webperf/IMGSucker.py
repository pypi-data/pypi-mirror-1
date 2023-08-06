#
# Copyright (c) 2002 ekit.com Inc (http://www.ekit-inc.com/)
# Copyright (c) 2001 Bizar Software Pty Ltd (http://www.bizarsoftware.com.au/)
#
# See the README for full license details.
# 
# $Id: IMGSucker.py,v 1.1 2002/06/11 07:14:40 richard Exp $

import htmllib, formatter, urlparse, thread, threading, Queue

class IMGSucker(htmllib.HTMLParser):
    '''Suck in all the images and linked stylesheets for an HTML page.

    The sucker uses a HTTP session object which provides:
         url - the URL of the page that we're parsing
     session - a HTTP session object which provides:
               fetch: a method that retrieves a file from a URL
               images: a mapping that holds the fetched images

    Once instantiated, the sucker is fed data through its feed method and
    then it must be close()'ed.
    '''
    def __init__(self, url, session, num_threads):
        htmllib.HTMLParser.__init__(self, formatter.NullFormatter())
        self.base = url
        self.session = session
        self.savedata = self.output = ""

        # queue of stuff to fetch - making sure we don't double-up
        self.fetch_queue = Queue.Queue()
        self.fetch = {}

        # stuff for keeping track of the threads
        self.num_threads = 4
        self.finished_threads = 0
        self.finished_threads_lock = threading.Lock()
        self.finished = threading.Event()
        self.finished.clear()

        # start up the requested number of threads to fetch the images
        self.num_threads = num_threads
        for i in range(self.num_threads):
            thread.start_new_thread(self.fetchingThread, ())

    def fetchingThread(self):
        #print thread.get_ident(), 'fetchingThread'
        url = self.fetch_queue.get()
        while url:
            try:
                #print thread.get_ident(), '... url', url
                self.session.GET(url)
            except self.session.HTTPError:
                pass
            url = self.fetch_queue.get()
        #print thread.get_ident(), '... all done'
        self.threadFinished()

    def threadFinished(self):
        self.finished_threads_lock.acquire()
        self.finished_threads += 1
        if self.finished_threads == self.num_threads:
            self.finished.set()
        self.finished_threads_lock.release()

    def appendFetch(self, url):
        if self.fetch.has_key(url):
            return
        self.fetch[url] = 0
        self.fetch_queue.put(url)

    def close(self):
        #print 'close'
        htmllib.HTMLParser.close(self)
        # flush the queue using blanks
        for i in range(self.num_threads):
            self.fetch_queue.put('')  

    def handle_starttag(self, tag, method, attributes):
        if tag == 'img' or tag == 'base' or tag == 'link':
            method(attributes)

    def do_base(self, attributes):
        for name, value in attributes:
            if name == 'href':
                self.base = value

    def do_img(self, attributes):
        for name, value in attributes:
            if name == 'src':
                self.appendFetch(urlparse.urljoin(self.base, value))

    def do_link(self, attributes):
        for name, value in attributes:
            if name == 'href':
                self.appendFetch(urlparse.urljoin(self.base, value))

#
# $Log: IMGSucker.py,v $
# Revision 1.1  2002/06/11 07:14:40  richard
# initial
#
#
# vim: set filetype=python ts=4 sw=4 et si

