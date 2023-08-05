##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Task Service Implementation

$Id: service.py 81533 2007-11-05 16:57:26Z fdrake $
"""
__docformat__ = 'restructuredtext'

import datetime
import logging
import persistent
import threading
import time
import zc.queue
import zope.interface
import zope.publisher.base
import zope.publisher.publish
from BTrees.IOBTree import IOBTree
from zope import component
from zope.app import zapi
from zope.app.appsetup.product import getProductConfiguration
from zope.app.container import contained
from zope.app.component.interfaces import ISite
from zope.app.publication.zopepublication import ZopePublication
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import traverse
from zope.component.interfaces import ComponentLookupError
from lovely.remotetask import interfaces, job, task

log = logging.getLogger('lovely.remotetask')

storage = threading.local()


class TaskService(contained.Contained, persistent.Persistent):
    """A persistent task service.

    The available tasks for this service are managed as utilities.
    """
    zope.interface.implements(interfaces.ITaskService)

    taskInterface = interfaces.ITask

    _scheduledJobs  = None
    _scheduledQueue = None

    def __init__(self):
        super(TaskService, self).__init__()
        self._counter = 1
        self.jobs = IOBTree()
        self._queue = zc.queue.PersistentQueue()
        self._scheduledJobs = IOBTree()
        self._scheduledQueue = zc.queue.PersistentQueue()

    def getAvailableTasks(self):
        """See interfaces.ITaskService"""
        return dict(component.getUtilitiesFor(self.taskInterface))

    def add(self, task, input=None):
        """See interfaces.ITaskService"""
        if task not in self.getAvailableTasks():
            raise ValueError('Task does not exist')
        jobid = self._counter
        self._counter += 1
        newjob = job.Job(jobid, task, input)
        self.jobs[jobid] = newjob
        self._queue.put(newjob)
        newjob.status = interfaces.QUEUED
        return jobid

    def addCronJob(self, task, input=None,
                   minute=(),
                   hour=(),
                   dayOfMonth=(),
                   month=(),
                   dayOfWeek=(),
                   delay=None,
                  ):
        jobid = self._counter
        self._counter += 1
        newjob = job.CronJob(jobid, task, input,
                minute, hour, dayOfMonth, month, dayOfWeek, delay)
        self.jobs[jobid] = newjob
        if newjob.delay is None:
            newjob.status = interfaces.CRONJOB
        else:
            newjob.status = interfaces.DELAYED
        self._scheduledQueue.put(newjob)
        return jobid

    def reschedule(self, jobid):
        self._scheduledQueue.put(self.jobs[jobid])

    def clean(self, stati=[interfaces.CANCELLED, interfaces.ERROR,
                           interfaces.COMPLETED]):
        """See interfaces.ITaskService"""
        allowed = [interfaces.CANCELLED, interfaces.ERROR,
                   interfaces.COMPLETED]
        for key in list(self.jobs.keys()):
            job = self.jobs[key]
            if job.status in stati:
                if job.status not in allowed:
                    raise ValueError('Not allowed status for removing. %s' % \
                        job.status)
                del self.jobs[key]

    def cancel(self, jobid):
        """See interfaces.ITaskService"""
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break
        if jobid in self.jobs:
            job = self.jobs[jobid]
            if (   job.status == interfaces.CRONJOB
                or job.status == interfaces.DELAYED
               ):
                job.status = interfaces.CANCELLED

    def getStatus(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].status

    def getResult(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].output

    def getError(self, jobid):
        """See interfaces.ITaskService"""
        return str(self.jobs[jobid].error)

    def startProcessing(self):
        """See interfaces.ITaskService"""
        if self.__parent__ is None:
            return
        if self._scheduledJobs == None:
            self._scheduledJobs = IOBTree()
        if self._scheduledQueue == None:
            self._scheduledQueue = zc.queue.PersistentQueue()
        path = [parent.__name__ for parent in zapi.getParents(self)
                if parent.__name__]
        path.reverse()
        path.append(self.__name__)
        path.append('processNext')

        thread = threading.Thread(
            target=processor, args=(self._p_jar.db(), path),
            name=self._threadName())
        thread.setDaemon(True)
        thread.running = True
        thread.start()

    def stopProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is None:
            return
        name = self._threadName()
        for thread in threading.enumerate():
            if thread.getName() == name:
                thread.running = False
                break

    def isProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is not None:
            name = self._threadName()
            for thread in threading.enumerate():
                if thread.getName() == name:
                    if thread.running:
                        return True
        return False

    def _threadName(self):
        """Return name of the processing thread."""
        # This name isn't unique based on the path to self, but this doesn't
        # change the name that's been used in past versions.
        path = [parent.__name__ for parent in zapi.getParents(self)
                if parent.__name__]
        path.append('remotetasks')
        path.reverse()
        path.append(self.__name__)
        return '.'.join(path)

    def processNext(self, now=None):
        job = self._pullJob(now)
        if job is None:
            return False
        try:
            jobtask = component.getUtility(self.taskInterface, name=job.task)
        except ComponentLookupError, error:
            log.error('Task "%s" not found!'% job.task)
            log.exception(error)
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
            return True
        job.started = datetime.datetime.now()
        if not hasattr(storage, 'runCount'):
            storage.runCount = 0
        storage.runCount += 1
        try:
            job.output = jobtask(self, job.id, job.input)
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.COMPLETED
        except task.TaskError, error:
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
        except Exception, error:
            if storage.runCount <= 3:
                log.error(
                    'catched a generic exception, preventing thread from crashing')
                log.exception(error)
                raise
            else:
                job.error = error
                if job.status != interfaces.CRONJOB:
                    job.status = interfaces.ERROR
        job.completed = datetime.datetime.now()
        storage.runCount = 0
        return True

    def process(self, now=None):
        """See interfaces.ITaskService"""
        while self.processNext(now):
            pass

    def _pullJob(self, now=None):
        # first move new cron jobs from the scheduled queue into the cronjob
        # list
        if now is None:
            now = int(time.time())
        while len(self._scheduledQueue)>0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        # try to get the next cron job
        while True:
            try:
                first = self._scheduledJobs.minKey()
            except ValueError:
                break
            else:
                if first > now:
                    break
                jobs = self._scheduledJobs[first]
                job = jobs[0]
                self._scheduledJobs[first] = jobs[1:]
                if len(self._scheduledJobs[first]) == 0:
                    del self._scheduledJobs[first]
                if (    job.status != interfaces.CANCELLED
                    and job.status != interfaces.ERROR
                   ):
                    if job.status != interfaces.DELAYED:
                        self._insertCronJob(job, now)
                    return job
        # get a job from the input queue
        if self._queue:
            return self._queue.pull()
        return None

    def _insertCronJob(self, job, now):
        for callTime, scheduled in list(self._scheduledJobs.items()):
            if job in scheduled:
                scheduled = list(scheduled)
                scheduled.remove(job)
                if len(scheduled) == 0:
                    del self._scheduledJobs[callTime]
                else:
                    self._scheduledJobs[callTime] = tuple(scheduled)
                break
        nextCallTime = job.timeOfNextCall(now)
        job.scheduledFor = datetime.datetime.fromtimestamp(nextCallTime)
        set = self._scheduledJobs.get(nextCallTime)
        if set is None:
            self._scheduledJobs[nextCallTime] = ()
        jobs = self._scheduledJobs[nextCallTime]
        self._scheduledJobs[nextCallTime] = jobs + (job,)


class ProcessorPublication(ZopePublication):
    """A custom publication to process the next job."""

    def traverseName(self, request, ob, name):
        return traverse(removeSecurityProxy(ob), name, None)


def processor(db, path):
    """Job Processor

    Process the jobs that are waiting in the queue. This processor is meant to
    be run in a separate process; however, it simply goes back to the task
    service to actually do the processing.
    """
    path.reverse()
    while threading.currentThread().running:
        request = zope.publisher.base.BaseRequest(None, {})
        request.setPublication(ProcessorPublication(db))
        request.setTraversalStack(path)
        try:
            zope.publisher.publish.publish(request, False)
            if not request.response._result:
                time.sleep(1)
        except:
            # This thread should never crash, thus a blank except
            pass

def getAutostartServiceNames():
    """get a list of services to start"""

    serviceNames = []
    config = getProductConfiguration('lovely.remotetask')
    if config is not None:
        serviceNames = [name.strip()
                        for name in config.get('autostart', '').split(',')]
    return serviceNames


def bootStrapSubscriber(event):
    """Start the queue processing services based on the
       settings in zope.conf"""

    serviceNames = getAutostartServiceNames()

    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    # we assume that portals can only added at site root level

    log.info('handling event IStartRemoteTasksEvent')

    for siteName, serviceName in [name.split('@')
                                  for name in serviceNames if name]:
        if siteName == '':
            sites = [root_folder]
        elif siteName == '*':
            sites = []
            sites.append(root_folder)
            for folder in root_folder.values():
                if ISite.providedBy(folder):
                    sites.append(folder)
        else:
            sites = [root_folder.get(siteName)]

        rootSM = root_folder.getSiteManager()
        rootServices = list(rootSM.getUtilitiesFor(interfaces.ITaskService))

        for site in sites:
            csName = getattr(site, "__name__", '')
            if csName is None:
                csName = 'root'
            if site is not None:
                sm = site.getSiteManager()
                if serviceName == '*':
                    services = list(sm.getUtilitiesFor(interfaces.ITaskService))
                    if siteName != "*" and siteName != '':
                        services = [s for s in services
                                       if s not in rootServices]
                else:
                    services = [(serviceName,
                                 component.queryUtility(interfaces.ITaskService,
                                                       context=site,
                                                       name=serviceName))]
                serviceCount = 0
                for srvname, service in services:
                    if service is not None and not service.isProcessing():
                        service.startProcessing()
                        serviceCount += 1
                        msg = 'service %s on site %s started'
                        log.info(msg % (srvname, csName))
                    else:
                        if siteName != "*" and serviceName != "*":
                            msg = 'service %s on site %s not found'
                            log.error(msg % (srvname, csName))
            else:
                log.error('site %s not found' % siteName)

        if (siteName == "*" or serviceName == "*") and serviceCount == 0:
            msg = 'no services started by directive %s'
            log.warn(msg % name)
