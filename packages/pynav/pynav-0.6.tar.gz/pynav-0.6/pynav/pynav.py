#!/usr/bin/python
#  -*- coding=utf-8 -*-
'''
Created on 15 nov. 2009

@author: Sloft

Licence : GNU General Public License (GPL)
'''

from __future__ import with_statement #for Python 2.5 compatibility
import urllib
import urllib2
import cookielib
import re
import time
import random
import socket
import os
try:
    import cPickle as pickle
except:
    import pickle

class Pynav(object):
    """Programmatic web browser to fetch data and test web sites"""

    verbose = False
    
    def __init__(self, timeout=None, proxy=None):
        """ Constructor, many attributes can be used """
        self.temps_min = 0
        self.temps_max = 0
        self.max_page_size = 500000
        self.max_history = 200
        self.verbose = False
        self.__set_user_agents_list()
        self.user_agent = self.user_agent_list['firefox']['windows']
        self.__headers = {'User-Agent' : self.user_agent}
        self.__auto_referer = False
        self.__cookie_jar = cookielib.CookieJar()
        self.proxy = proxy
        self.__url_opener = urllib2.build_opener(*self.__get_handlers())
        self.history = []
        self.current_page = -1
        self.page_document_type = None
        self.page_info = None
        self.real_url = None
        self.relative_url = None
        self.base_url = None
        self.response = None
        self.download_path = os.getcwd()
        if timeout:
            socket.setdefaulttimeout(timeout)
    
    def __get_handlers(self):
        """Private method to get all handlers needed"""
        handlers = []
        handlers.append(urllib2.HTTPCookieProcessor(self.__cookie_jar))
        if self.proxy:
            handlers.append(urllib2.ProxyHandler({'http': self.proxy}))
        return handlers
       
    def __set_user_agents_list(self):
        """Private method to set the user agents list"""
        self.user_agent_list = {}
        self.user_agent_list['firefox'] = \
        {'windows' : 'Mozilla/5.0 (Windows; U; Windows NT 6; fr; rv:1.9.1.5) Gecko/Firefox/3.5.5'}
        self.user_agent_list['ie'] = {'windows' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Win64; x64; Trident/4.0)'}
    
    def set_http_auth(self, base_url, username, password):
        """Define parameters to set HTTP Basic Authentication"""
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, base_url, username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        self.__url_opener.add_handler(handler)

    def __set_referer(self, referer):
        """Decorator to define a referer, the previous visited page"""
        self.__headers['Referer'] = referer
    
    def __get_referer(self):
        """Decorator to get the referer, the previous visited page"""
        if self.__headers.has_key('Referer'):
            return self.__headers['Referer']
        else:
            return None
    
    referer = property(__get_referer, __set_referer)

    def __set_auto_referer(self, auto_referer):
        """Decorator to set the status of the auto_referer attribute"""
        self.__auto_referer = auto_referer
        if not auto_referer:
            if self.__headers.has_key('Referer'):
                self.__headers.pop('Referer')
    
    def __get_auto_referer(self):
        """Decorator to get the status of the auto_referer attribute"""
        return self.__auto_referer
    
    autoReferer = property(__get_auto_referer, __set_auto_referer)
    
    def save_history(self, file_name):
        """Save history in a file"""
        with open(file_name, 'w') as f:
            pickle.dump(self.history, f)
    
    def load_history(self, file_name):
        """Load history from a file"""
        try:
            with open(file_name, 'r') as f:
                self.history = pickle.load(f)
        except IOError:
            print "ERROR: file", file_name, "doesn't exist"

    def __init_go(self):
        """Private method to initialize some attributes"""
        sleep_time = random.randint(self.temps_min, self.temps_max)
        if self.verbose and sleep_time > 0:
            print 'waiting', sleep_time, 'secs'
        if sleep_time:
            time.sleep(sleep_time)
        if self.__auto_referer:
            if len(self.history) > 0:
                self.referer = self.history[self.current_page]['url']
    
    def go(self, url, values = {}):
        """Visite a web page, post values can be used"""
        self.__init_go()
        
        if not re.search('://', url):
            url = 'http://' + url
        
        if url.count('/') < 3:
            url = url + '/'
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, self.__headers)
        
        self.response = None
        
        handle = None
        try:
            handle = self.__url_opener.open(req)
        except urllib2.HTTPError, exc:
            if exc.code == 404:
                print 'ERROR: Page not found !'
            else:           
                print "ERROR: HTTP request failed with error %d (%s)" % (exc.code, exc.msg)
        except urllib2.URLError, exc:
            print "ERROR: Opening URL failed because:", exc.reason
        
        if handle:
            self.response = handle.read(self.max_page_size)
            self.page_document_type = handle.info().getheader("Content-Type","")
            self.page_info = handle.info()
            self.real_url = handle.geturl()
            
            if len(self.history) > self.max_history - 1:
                del self.history[0]
            self.current_page = self.current_page + 1
            self.history.append({'url':url, 'post':values, 'response':self.response})
            
            if self.current_page > len(self.history) - 1:
                self.current_page = len(self.history) - 1
            
            self.relative_url = self.real_url.replace(self.real_url.split('/')[-1], '')
            self.base_url = 'http://'+self.real_url[7:].split('/')[0]+'/'
            return self.response
        else:
            return None #Exception ?
    
    def replay(self, begining=0, end=None, print_url=False, print_post=False,
               print_response=False):
        """Replay history, can be used after loading history from a file"""
        history, self.history = self.history, []
        if not end:
            end = len(history)
        for page in history[begining:end]:
            self.go(page['url'], page['post'])
            if print_url:
                print page['url']
            if print_post:
                print page['post']
            if print_response:
                print page['response']
    
    def search(self, reg):
        """Search a regex in the page, return a boolean"""
        return re.search(reg, self.response)
    
    def find(self, reg):
        """Return the result found by the regex"""
        res = re.findall(reg, self.response, re.S)
        if len(res)==1:
            return res[0]
        else:
            return res
    
    def find_all(self, reg):
        """Return all results found by the regex"""
        return re.findall(reg, self.response, re.S)
    
    def download(self, url, destination=None):
        """Download the file at a url to a file or destination"""
        if not destination:
            destination = self.download_path
        
        if os.path.isdir(destination):
            if destination[-1] in ('/', '\\'):
                destination = destination + url.split('/')[-1]
            else:
                destination = destination + '/' + url.split('/')[-1]
        else:
            destination = self.download_path + destination

        if self.verbose:
            print 'Downloading to:', destination
        return urllib.urlretrieve(url, destination)

    def save_response(self, destination):
        """Save the page to a file"""
        f = open(destination, 'w')
        try:
            f.write(self.response)
        finally:
            f.close()
    
    def cookie_exists(self, name='PHPSESSID'):
        """Test if a cookie exists"""
        return name in [cookie.name for cookie in self.__cookie_jar]
    
    def add_path(self, url):
        """Correct an url depending on the link, internal use"""
        if re.search('://', url):
            return url
        else:
            if url[0] == '/':
                return self.base_url[:-1]+url
            else:
                return self.relative_url+url
    
    def get_all_links(self, reg = None):
        """Return a list of all links found, a regex can be used"""
        links = re.findall('href="(.*?)"', self.response)
        if reg:
            def match(link): return len(re.findall(reg, link)) > 0
            return [self.add_path(link) for link in links if match(link)]
        else:
            return [self.add_path(link) for link in links]
    
    def get_all_images(self, reg = None):
        """Return a list of all images found, a regex can be used"""
        images = re.findall('img.*?src="(.*?)"', self.response)
        if reg:
            def match(image): return len(re.findall(reg, image)) > 0
            return [self.add_path(image) for image in images if match(image)]
        else:
            return [self.add_path(image) for image in images]
    
    def set_page_delay(self, temps_min=0, temps_max=0):
        """Define the time between pages, random seconds, min and max"""
        self.temps_min = temps_min
        if(temps_min > temps_max):
            self.temps_max = temps_min
        else:
            self.temps_max = temps_max
        if self.verbose:
            print 'temps_min:', self.temps_min, ', temps_max:', self.temps_max

    def strip_tags(self, html):
        """Strip all tags of an HTML string and return only texts"""
        intag = [False]
        def chk(c):
            if intag[0]:
                intag[0] = (c != '>')
                return False
            elif c == '<':
                intag[0] = True
                return False
            return True
        return ''.join(c for c in html if chk(c))
