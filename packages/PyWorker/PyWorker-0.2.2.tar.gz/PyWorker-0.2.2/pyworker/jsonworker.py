#!/usr/bin/python
# -*- coding: utf-8 -*-

# Most workers are expected to use JSON msgs
import simplejson

from pyworker import STATUSES, Worker, WorkerResponse, WorkerException, JsonMsgParseError

class JSONWorker(Worker):
    """Similar in practice to the normal Worker, except it only tolerates JSON
    messages and will ignore any it cannot parse.
    Passing it an outbound queue will allow it to pass any unparsable msgs onwards."""
    def run(self):
        while (True):
            # Blocking call:
            if self.stop:
                break
            msg = self.queue_stdin.get()
            # TODO implement variable timeout on .starttask() method
            try:
                jmsg = simplejson.loads(msg)
                resp = self.starttask(jmsg)
                self.endtask(jmsg, resp)
            except Exception, e:
                print "Failed to parse\n%s" % msg
                print e
                if self.queue_stdout:
                    self.queue_stdout.put(msg)
                # Actively consume bad messages
                self.queue_stdin.task_done()

