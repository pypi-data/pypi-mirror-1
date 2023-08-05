# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from threading import Thread, Lock
from Queue import Queue, Empty
from collections import deque
import time, random, sys, traceback
import stellaris

log = stellaris._logger

class Worker(Thread):

    def __init__(self, queue, id, scheduler, sleeptime = 0.5):
        Thread.__init__(self)
        self.queue = queue
        self.scheduler = scheduler
        self.__active = False
        self.sleeptime = sleeptime
        self.wid = id
        self.setDaemon(True)
#        self.tasks = TaskQueue()
        self.start()

    def id(self):
        return self.wid
                
    def run(self):
        # make sure that the queue is finished before
        # a thread is killed, all-or-nothing semantics
        # is necessary...
        self.__active = True
        while self.__active:
            try:
                # receive a new task from the queue, wait for sleeptime seconds
                # before reporting empty and exiting
                task = self.queue.get(True, self.sleeptime)
                log.debug(str(self) + " retrieved task " + str(task))
                    
                try:
                    ts = time.clock()
                    task.execute()
                except Exception, e:
                    task.error(e)
                    
                log.debug(str(self) + " finished task " + str(task) + " after " + str(time.clock()-ts) + " seconds")
            except Empty,e:
                # this is a bad thing(TM)
                sys.exc_clear()
                
                # this worker is done
                # let the scheduler know and then quit
                
                #self.scheduler.notifyDone(self)
                #self.active = False
                #return
                
                # give the other workers a chance to run
            time.sleep(0.1)
        
        #log.debug('%s finished execution', str(self))
                    
    def __str__(self):
        return "Worker_" + str(self.wid)

    def isActive(self):
        return self.__active
                
    def stop(self):
        self.__active = False


class TaskFactory:

    def __init__(self):
        self.id = 0

    def create(self, finishedCb, f, args, kwargs):
        self.id += 1
        return Task(self.id, finishedCb, f, args, kwargs)
                
class Task:

    def __init__(self, id, finishedCb, f, args, kwargs, dependencies=[]):
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.finishedCb = finishedCb
        self.ts = None
        self.taskid = id
        self.active = False
        
        # this task will not execute until all given dependencies
        # are finished, list of tasks
        self.deps = set()
        for t in dependencies:
            if not t == self.taskid:
                self.deps.add(t)
    
        # list of tasks that are waiting for this task to finish
        # make sure they are notified when done
        self.waiting = []
    
    def dependsOn(self, t):
        #log.debug("Adding dependency " + str(self) + " -> " + str(t))
        if not t.taskid == self.taskid:
            # when adding dependency, make the other task know the
            # this task is waiting
            self.deps.add(t.taskid)
            t.addWaiting(self)
            
    def removeDependency(self, taskid):
        #log.debug("Removing dependency " + str(self) + " -> " + str(taskid) + ", " + str(self.deps))    
        if taskid in self.deps:
            self.deps.remove(taskid)
        
    def addWaiting(self, t):
        self.waiting.append(t)
    
    def notifyWaiting(self):
        # remove me from the dependency list of all tasks waiting for me
        for wt in self.waiting:
            #log.debug("Notification " + str(self) + " -> " + str(wt))
            
            wt.removeDependency(self.taskid)            
    
    def hasDependencies(self):
        if len(self.deps) > 0:
            return True
        return False
                                    
    def execute(self):
        self.active = True    
        self.ts = time.clock()
        log.debug('Executing %s', str(self))
        result = self.f(*self.args, **self.kwargs)
            # should the depending tasks be notified from here?
            # all waiting tasks must exist.
        
            # should this be called in this thread or collected somehow else?
            
            #print "Calling callback: ", self.finishedCb
#        try:
        self.finishedCb(self, result)
#        except Exception, e:
#            raise Exception(e)

        self.notifyWaiting()
            #print "calling callback done!!"
        self.active = False
                        

    def id(self):
        return self.taskid

    def error(self, error):
        #print sys.exc_info()
        #log.debug(traceback.print_exc())
        log.debug(str(self) + " failed: " + str(error))
        self.finishedCb(self, error)
#        self.errorCb(self, error)
        # make sure all depending tasks also runs...?
        self.notifyWaiting()
            #print "calling callback done!!"
        self.active = False

    def __repr__(self):
        return "Task-" + str(self.taskid) + " {" + str(self.deps) + "}"
                
class Scheduler(Thread):
    
    def __init__(self, maxworkers=32):
        Thread.__init__(self)
        self.__running = False
        self.__shutdown = False
        
        # no limit on number of queue items
        self.execqueue = Queue(0)
        self.waitqueue = deque()
        
        self.maxworkers = maxworkers
        self.workers = {}
              
        self.workerid = 1
        
        for i in range(0, self.maxworkers):
            self._createWorker()

        self.setDaemon(True)
        self.start()

    def notifyDone(self, worker):
        # the worker is done remove all local state about the worker
        #if worker.id() in self.workers:
        #    del self.workers[worker.id()]
        pass
            
    def _createWorker(self):
        w = Worker(self.execqueue, self.workerid, self)
        self.workers[w.id()] = w
        self.workerid += 1
        return w

    # tasks that are depending on each other
    # must be placed in the same queue to guarantee
    # sequential execution
    def enqueue(self, task):
        if not self.__shutdown:
            self.waitqueue.append(task)
#            self.waitqueue[task.id()] = task

    def run(self):
        self.__running = True
        while self.__running:

            try:
                task = self.waitqueue[0]
                log.debug("task: %s", str(task))
                if not task.hasDependencies():
                    self.execqueue.put(self.waitqueue.popleft())
            
                self.waitqueue.rotate(-1)
            except:
                # don't do anything when the waitqueue is empty
                pass
                        
#            waiting = []
            time.sleep(0.1)
            
    def stop(self):
        # when shutting down, no new tasks will be allowed...
        self.__shutdown = True
        
        #print "joining!"
        #self.execqueue.join()
        # block until all tasks in the execqueue are done
#        print self.waitqueue
        while len(self.waitqueue) > 0 and self.execqueue:
            time.sleep(0.1)
        
        for worker in self.workers:
            self.workers[worker].stop()
            self.workers[worker].join()
                
        self.__running = False
        self.join()
        log.info("Scheduler shutdown complete")
        
if __name__ == "__main__":
    import random, sys
    
    s = Scheduler(4)

    def blub(a, b=12):
        i = 0
        #time.sleep(random.randint(1,2))
        return a+b

    def done(task, result):
        #print task, result
        pass
   
    def error(task, result):
        print "error: ", task, result
        
    i = 0
    tasks = TaskFactory()
    queues = [None, "blub", "test"]

    tasklist = []
    t_prev = None
    for i in range(0,10):
        t = tasks.create(done, blub, [i], {'b':0})
        if t_prev:
            t.dependsOn(t_prev)        
        tasklist.append(t)
        t_prev = t
        
    t1 = tasks.create(done, blub, [1], {'b':100})
    t2 = tasks.create(done, blub, [2], {'b':100})
    t3 = tasks.create(done, blub, [3], {'b':100})
    t4 = tasks.create(done, blub, [4], {'b':100})
    t5 = tasks.create(done, blub, [5], {'b':100})
    t6 = tasks.create(done, blub, [6], {'b':100})        
#    tasklist = [t1, t2, t3, t4, t5, t6]
#    tasklist += [ (t5, "blub"), (t6, "test")]

    t2.dependsOn(t1)
    t3.dependsOn(t1)
    t2.dependsOn(t3)
    t4.dependsOn(t2)
    t5.dependsOn(t2)
    t6.dependsOn(t2)
    # queues are re-arranged internally, an explicit dependency has
    # higher precedence than a queue dependency    
#    tasklist = [(t1,"1"), (t2, "2"), (t3, "3"), (t4, "4")]    
#    tasklist += [(t5, "5"), (t6, "6")]
    
    for t in tasklist:
        #print "Enqueuing", t
        s.enqueue(t)
        
#    while i < 3:
#        time.sleep(random.randint(0,5))
        
#        print "entering round: ", i
#        for k in range(0,random.randint(1,5)):
#            t = tasks.create(done, blub, [random.randint(20,30)], {'b': random.randint(0,1000)})
#            q = queues[random.randint(0, len(queues)-1)]
#            print "Enqueuing", t, "in queue", q
#            s.enqueue(t, q)
#        i+=1

    s.stop()    
