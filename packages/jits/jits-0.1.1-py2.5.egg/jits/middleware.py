import datetime

import scheduler

class JitsMiddleware(object):
    def __init__(self):
        from django.conf import settings
        self.scheduler = scheduler.Scheduler(getattr(settings, 'JITS_THREADED', False),
                                                 getattr(settings, 'JITS_NUM_THREADS', 10),
                                                 )

        self.delta = datetime.timedelta(seconds=getattr(settings, 'JITS_MIN_SECONDS', 5), 
                                        minutes=getattr(settings, 'JITS_MIN_MINUTES', 0))
        self.last_check = datetime.datetime(2000, 1, 1, 1, 1, 1)
        
    def process_request(self, request):
        now = datetime.datetime.now()
        if now - self.last_check > self.delta:
            self.last_check = now
            self.scheduler.poll()
        return None

