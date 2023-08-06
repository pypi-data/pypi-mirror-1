#!/usr/bin/python
# -*- coding: utf-8 -*-

# Most workers are expected to use JSON msgs
import simplejson

STATUSES = {'FAIL':0,
            'COMPLETE':1,
            }

# shorthand
FAIL = STATUSES['FAIL']
COMPLETE = STATUSES['COMPLETE']

class WorkerResponse(object):
    def __init__(self, status, **kw):
        self.status = status
        self.context = kw

class JsonMsgParseError(Exception):
    """JSON passed as a message over the queue couldn't be decoded."""
    pass

class WorkerException(Exception):
    def __init__(self, response=None):
        self.response = response
    def __str__(self):
        if self.response:
            resp_string = "Worker failed with a status: %s" % (STATUSES[self.response.status])
            if self.response.context:
                resp_string += "\n Context: %s" % self.response.context
        else:
            return "Worker failed"

class Worker(object):
    def __init__(self, queue_stdin, queue_stdout=None, **kw):
        """Base class for all the workers.
        queue_stdin - the instance passed through queue_stdin should implement a
        *blocking* .get(), .task_done() and __len__().
        queue_stdout - the instance passed should implement a blocking .put() and
        non-blocking __len__()

        The built-in python module "Queue" can produce suitable queue objects, eg:

        >>> from Queue import Queue
        >>> import Thread
        >>> q = Queue()
        >>> for i in range(num_worker_threads):
        ...      t = Thread(target=Worker(q))
        ...      t.setDaemon(True)
        ...      t.start()
        >>> for item in source():
        ...      q.put(item)

        Queue's produced by the companion module, AMQPQueue, will also work well:

        >>> from amqpqueue import QueueFactory
        >>> import Thread
        # Make a queue factory and point it at the local AMQP server
        >>> qf = QueueFactory('localhost:5672','guest','guest')
        >>> producer = qf.Producer('my_queue')
        >>> for i in range(num_worker_threads):
        ...      t = Thread(target=Worker(qf.Consumer('my_queue')))
        ...      t.setDaemon(True)
        ...      t.start()
        >>> for item in source():
        ...      producer.put(item)

        Other keyword parameters can be passed to the workers as necessary, and these are
        accessible via a self.context dictionary, eg:
        >>> w = MyWorker(q_in, q_out, foo=bar)
        ...
        (In the worker instance:)
        >>> if self.context.get('foo'):
        >>>     print self.context['foo']
        /'bar'/

        In actual use, the starttask and/or endtask method should be overridden to perform
        the tasks necessary.

        Overwrite the .starttask(msg) method, which is passed the contents of the message from
        the queue. If this is the only method overridden, it is necessary to return a
        WorkerResponse object (or any object with a obj.status => 0 for FAIL or 1 for COMPLETE)

        endtask(msg, response) can likewise be overridden to perform tasks
         - BUT this must acknoledge the msg via a .task_done() on the 'in' queue
         -> self.queue_stdin.

        endtask is typically the method to override for simple atomic-style operations.
        """
        self.queue_stdin = queue_stdin
        self.queue_stdout = queue_stdout
        self.context = kw
        self.stop = False
        if 'start' in kw:
            self.run()

    def __del__(self):
        # Attempt to clean up after self
        try:
            self.queue_stdin.close()
        except:
            pass

    def parse_json_msg(self, msg, encoding="UTF-8"):
        try:
            return simplejson.loads(msg,encoding=encoding)
        except:
            raise JsonMsgParseError

    def run(self):
        while (True):
            # Blocking call:
            if self.stop:
                break
            msg = self.queue_stdin.get()
            # TODO implement variable timeout on .starttask() method
            resp = self.starttask(msg)
            self.endtask(msg, resp)

    def starttask(self, msg):
        """Implements a basic 'echo' worker - pointless, but illustrative.
        This method should be overridden by a specific worker class."""
        return WorkerResponse(COMPLETE)

    def endtask(self, msg, response):
        """Simple task end, ack'ing the message consuming it on a COMPLETE response."""
        if response.status == FAIL:
            raise WorkerException(resp)
        elif response.status == COMPLETE:
            if self.queue_stdout:
                self.queue_stdout.put(msg)
            else:
                # eg print msg
                pass
            self.queue_stdin.task_done()

class PollingWorker(Worker):
    def __init__(self, queue_stdin, queue_stdout=None, polling_wait=60, **kw):
        """PollingWorker is built on the base Worker class.

        The main difference is that it doesn't expect that the 'queue-in' object
        will provide a get method that blocks until it recieves a message.

        It will wait for 'polling_time' (default: 60 seconds) and then call the get
        method. If the method returns a value that evaluates to False, then the worker
        is put to sleep for the polling_time again to try again.

        The wait is performed by "time.sleep(polling_wait)"

        If a message of any sort is received, then the message is passed through the normal
        pattern of starttask/endtask.
        """
        self.queue_stdin = queue_stdin
        self.queue_stdout = queue_stdout
        # Make sure that the time is in seconds:
        assert (isinstance(polling_wait, int) or isinstance(polling_wait, float)), "polling_wait must be either an integer or a float"
        self.polling_wait = polling_wait
        self.context = kw
        self.stop = False
        if 'start' in kw:
            self.run()

    def run(self):
        while (True):
            # Non-blocking call:
            if self.stop:
                break
            msg = self.queue_stdin.get()
            if msg:
                resp = self.starttask(msg)
                self.endtask(msg, resp)
            sleep(self.polling_wait)

