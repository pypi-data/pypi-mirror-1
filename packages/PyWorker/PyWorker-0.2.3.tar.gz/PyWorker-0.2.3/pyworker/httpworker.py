#!/usr/bin/python
# -*- coding: utf-8 -*-

# For the HTTPWorker
from urllib import urlencode
import httplib2

from pyworker import STATUSES, Worker, WorkerResponse, WorkerException, JsonMsgParseError

# For tempfile/ramfile handling:
# Unicode is highly likely, therefore StringIO > cStringIO
from StringIO import StringIO
from tempfile import mkstemp
from os import remove

class HTTPWorker(Worker):
    """Gets a local copy of the resource at the URL in the JSON msg ('url') and simply
    prints the first "line".
    
    Handles an HTTP cache, so that multiple HTTPWorkers performing different tasks
    on the same resource will not cause multiple calls to the same resource, unless
    the E-Tag header is different.
    
    If the E-Tag header is different, the updated resource is downloaded and passed
    instead.
    
    It is expected that self.endtask will be overwritten. 
    
    If the tempfile option is set, remember to delete the temporary file 
    as well as ack the msg! Eg -
    ------------------------------------------------------------
    import os
    class SolrFeeder(HTTPWorker):
        def endtask(self, msg, response):
            try:
                # do stuff with response.context['fd'], the file-descriptor for the resource
            finally:
                response.context['fd'].close()
                if self.context.get('tempfile', False):
                   os.remove(response.context['tempfile'])
                self.queue_stdin.task_done()

    s = SolrFeeder(queue_stdin, queue_stdout=None, tempfile = True)
    ------------------------------------------------------------    
    If 'id' is passed in the message instead, then this is inserted into a template, set
    by instantiating this worker with the parameter 'http_template'. Normal python
    string formating applies ( template % id )
    
    Requires configuration parameters:
        http_template = template for the URL to GET
        """
    def _get_tempfile(self):
        return mkstemp()
    
    def _get_ramfile(self):
        return (StringIO(), None)
    
    def httpsetup(self):
        self.http_template = self.context.get('http_template', None)
        self.h = httplib2.Http()
        self.method = self.context.get('method', 'GET')
        self.data_method = self.context.get('method', 'GETURL')
        if self.context.get('tempfile', False):
            self.tempfile = self._get_tempfile
        else:
            self.tempfile = self._get_ramfile
            
        self.setup = True
    
    def starttask(self, msg):
        """This will very simply GET the url supplied and pass the temp/ramfile to endtask"""
        try:
            if not self.setup:
                self.httpsetup()
            (fd, name) = self.tempfile()
            jmsg = self.parse_json_msg(msg)
            # Prepare HTTP request
            headers = {}
            if 'headers' in jmsg:
                headers = jmsg['headers']
            url = None
            if 'url' in jmsg:
                url = jmsg['url']
            elif 'id' in jmsg and self.http_template:
                url = self.http_template % jmsg['id']
            else:
               return WorkerResponse(FAIL)
            if not url:
                raise Exception("url not supplied")
            fd.write(h.request(jmsg['url'], "GET", headers=headers))
            fd.seek(0)
            return WorkerResponse(COMPLETE, fd=fd, tempfile=name, jmsg=jmsg, url=url)
        except Exception, e:
            return WorkerResponse(FAIL, exception = e)

    def endtask(self, msg, response):
        """Demo method to be overwritten. This simply reads the first 100 characters from
        the reponse.context['fd'] (file-handle) and deletes/removes the file."""
        try:
            first_bit = response.context['fd'].read(100)
            if self.queue_stdout:
                self.queue_stdout.put(first_bit)
            else:
                print "From url: %s, first 100 chars: \n %s" % (response.context['url'], first_bit)
        finally:
            response.context['fd'].close()
            if self.context.get('tempfile', False):
                remove(response.context['tempfile'])
            self.queue_stdin.task_done()
            
