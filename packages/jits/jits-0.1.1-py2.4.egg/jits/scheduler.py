import datetime
import logging

logger = logging.getLogger(__name__)

import threadpool

startup_tasks = []

class Scheduler(object):
    def __init__(self, threaded=False, numthreads=0):
        global scheduler_instance
        scheduler_instance = self
        
        self.threaded = threaded ; self.numthreads = numthreads
        if threaded:
            self.pool = threadpool.ThreadPool(numthreads)
        
        for task in startup_tasks:
            task()

    def poll(self):
        from app.models import Task
        tasks = Task.objects.filter(next_run__lte=datetime.datetime.now(), 
                                    running=False, expired=False)
        if tasks.count is 0:
            return None
        else:
            return self.run_tasks(tasks)
    
    def run_threaded_tasks(self, tasks):
        for task in tasks:
            self.poll.putRequest(threadpool.WorkRequest(self.run_task, args=[task]))

    def run_task(self, task):
        logger.debug('running task: '+str(task.name))
        try:
            result = task.callback()
        except:
            logger.exception('Callback for Task %s failed: ' % str(task.name))
        logger.info('Task '+str(task.name)+'Completed; Result: '+str(result))
        delta = datetime.timedelta(days=task.frequency_days, hours=task.frequency_hours,
                                   minutes=task.frequency_minutes, seconds=task.frequency_seconds)
        task.next_run = datetime.datetime.now() + delta
        task.running = False
        task.save()

    def run_tasks(self, tasks):
        # Optimized for queryset-refactor branch.
        tasks_to_run = list(tasks)
        if hasattr(tasks, 'update'):
            tasks.update(running=True)
        else:
            for t in tasks:
                t.running = True ; t.save()
            
        if self.threaded:
            return self.run_threaded_tasks(tasks_to_run)
        else:
            for task in tasks_to_run:
                self.run_task(task)
