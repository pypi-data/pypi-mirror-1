"""

  threading2:  like the standard threading module, but awesomer.

This module is designed as a drop-in replacement and extension for the default
"threading" module.  It has two main objectives:

    * implement primitives using native platform functionality where possible
    * expose more sophisticated functionality where if can be done uniformly

The following extensions are currently implemented:

    * ability to set (advisory) thread priority
    * thread groups for simultaneous management of multiple threads

The following API niceties are also included:

    * all blocking methods take a "timeout" argument and return a success code
    * all exposed objects are actual classes and can be safely subclassed

Planned extensions include:

    * ability to set (advisory) thread affinities
    * native events, semaphores and timed waits on win32
    * native conditions and timed waits on pthreads platforms

"""

from __future__ import with_statement


__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)



#  Expose some internal state of the threading module, for use by regr tests
from threading import _active,_DummyThread

#  Grab the best implementation we can use on this platform
import sys
try:
    if sys.platform == "win32":
        from threading2.t2_win32 import *
    else:
        from threading2.t2_posix import *
except ImportError:
    from threading2.t2_base import *
    del sys


__all__ = ["active_count","activeCount","Condition","current_thread",
           "currentThread","enumerate","Event","local","Lock","RLock",
           "Semaphore","BoundedSemaphore","Thread","ThreadGroup","Timer",
           "setprofile","settrace","stack_size","group_local"]


class ThreadGroup(object):
    """Object for managing many threads at once.

    ThreadGroup objects are a simple container for a set of threads, allowing
    them all to the managed as a single unit.  Operations that can be applied
    to a group include:

        * setting priority and affinity
        * joining and testing for liveness

    """

    def __init__(self,name=None):
        self.name = name
        self.__lock = Lock()
        self.__threads = set()
        self.__priority = None
        self.__affinity = None

    def __str__(self):
        if not self.name:
            return super(ThreadGroup,self).__str__()
        return "<ThreadGroup '%s' at %s>" % (self.name,id(self),)

    def _add_thread(self,thread):
        self.__threads.add(thread)

    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self,priority):
        """Set the priority for all threads in this group.

        If setting priority fails on any thread, the priority of all threads
        is restored to its previous value.
        """
        with self.__lock:
            old_priorities = {}
            try:
                for thread in self.__threads:
                    old_priorities[thread] = thread.priority
                    thread.priority = priority
            except Exception:
                for (thread,old_priority) in old_priorities.iteritems():
                    try:
                        thread.priority = old_priority
                    except Exception:
                        pass
                raise
            else:
                self.__priority = priority

    @property
    def affinity(self):
        return self.__affinity

    @affinity.setter
    def affinity(self,affinity):
        """Set the affinity for all threads in this group.

        If setting affinity fails on any thread, the affinity of all threads
        is restored to its previous value.
        """
        with self.__lock:
            old_affinities = {}
            try:
                for thread in self.__threads:
                    old_affinities[thread] = thread.affinity
                    thread.affinity = affinity
            except Exception:
                for (thread,old_affinity) in old_affinities.iteritems():
                    try:
                        thread.affinity = old_affinity
                    except Exception:
                        pass
                raise
            else:
                self.__affinity = affinity

    def is_alive(self):
        """Check whether any thread in this group is alive."""
        return any(thread.is_alive() for thread in self.__threads)
    isAlive = is_alive

    def join(self,timeout=None):
        """Join all threads in this group.

        If the optional "timeout" argument is given, give up after that many
        seconds.  This method returns True is the threads were successfully
        joined, False if a timeout occurred.
        """
        if timeout is None:
            for thread in self.__threads:
                thread.join()
        else:
            deadline = _time() + timeout
            for thread in self.__threads:
                delay = deadline - _time()
                if delay <= 0:
                    return False
                if not thread.join(delay):
                    return False
        return True


default_group = ThreadGroup()


class group_local(object):
    """Group-local storage object.

    Instances of group_local behave simlarly to threading.local() instance,
    except that the values of their attributes are common to all threads in 
    a single group.
    """

    def __init__(self):
        self.__lock = Lock()
        self.__group_locks = {}
        self.__attrs = {}

    def __getattr__(self,name):
        group = current_thread().group
        try:
            return self.__attrs[group][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self,name,value):
        group = current_thread().group
        try:
            lock = self._group_locks[group]
        except KeyError:
            with self.__lock:
                lock = self._group_locks.setdefault(group,Lock())
        with lock:
            try:
                self.__attrs[group][name] = value
            except KeyError:
                self.__attrs[group] = {}
                self.__attrs[group][name] = value

    def __delattr__(self,name):
        group = current_thread().group
        try:
            lock = self._group_locks[group]
        except KeyError:
            with self.__lock:
                lock = self._group_locks.setdefault(group,Lock())
        with lock:
            try:
                del self.__attrs[group][name]
            except KeyError:
                raise AttributeError(name)


#  Patch current_thread() and enumerate() to always return instances
#  of our extended Thread class.

_current_thread = current_thread
def current_thread():
    thread = _current_thread()
    if not isinstance(thread,Thread):
        thread = Thread.from_thread(thread)
    return thread
currentThread = current_thread

_enumerate = enumerate
def enumerate():
    threads = _enumerate()
    for i in xrange(len(threads)):
        if not isinstance(threads[i],Thread):
            threads[i] = Thread.from_thread(threads[i])
    return threads


