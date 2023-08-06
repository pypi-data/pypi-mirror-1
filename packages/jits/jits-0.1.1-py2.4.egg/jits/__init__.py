import middleware, app, scheduler

class AddTask(object):
    """Add task callable class"""
    def __init__(self, callback, name=None, days=0, hours=0, minutes=0, seconds=0, now=True):
        self.callback = callback
        self.name = name
        self.days = days ; self.hours = hours ; self.minutes = minutes ; self.seconds = seconds
        self.now = now
    
    def __call__(self):
        from app import models
        task = models.Task(callback=self.callback, name=self.name, frequency_days=self.days,
                           frequency_hours=self.hours, frequency_minutes=self.minutes,
                           frequency_seconds=self.seconds)
        if self.now is True:
            task.running = True
            task.save()
            scheduler.scheduler_instance.run_task(task)

def add_task(callback, name=None, days=0, hours=0, minutes=0, seconds=0, now=True):
    if now is True and hasattr(scheduler, 'scheduler_instance'):
        AddTask(callback, name, days, hours, minutes, seconds, now)()
    else:
        scheduler.startup_tasks.append(AddTask(callback, name, days, hours, minutes, seconds, now))
    
    
    
    


