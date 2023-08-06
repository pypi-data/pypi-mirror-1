from TGScheduler import scheduler
import atexit
import logging
log = logging.getLogger(__name__)

def start_scheduler():
    log.debug("Starting Scheduler")
    scheduler._start_scheduler()
    atexit.register(stop_scheduler)
    
def stop_scheduler():
    log.debug("Shutting down scheduler")
    scheduler._stop_scheduler()