from celery import Celery
from fabric import Connection
import redis
import time

celery = Celery("tasks", broker="redis://localhost:6379/", backend="redis://localhost:6379/")
r = redis.Redis()

def update_progress(task_id, status, output=""):
    r.set(f"progress:{task_id}", {
        "status": status,
        "output": output,
        "timestamp": time.time()
    })

def get_task_progress(task_id):
    data = r.get(f"progress:{task_id}")
    return eval(data) if data else {"status": "PENDING", "output": "", "timestamp": 0}

@celery.task(bind=True)
def run_fabric_command(self, host, cmd):
    update_progress(self.request.id, "RUNNING", "Starting SSH command...")
    try:
        with Connection(host) as c:
            for line in c.run(cmd, hide=True, pty=True, warn=True).stdout.splitlines():
                update_progress(self.request.id, "RUNNING", line)
                time.sleep(0.1)  # simulate streaming
        update_progress(self.request.id, "SUCCESS", "Command completed.")
    except Exception as e:
        update_progress(self.request.id, "FAILURE", str(e))
