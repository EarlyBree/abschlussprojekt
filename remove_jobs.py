from multiprocessing import connection
import redis
from rq import Queue
from rq.registry import FailedJobRegistry, StartedJobRegistry,ScheduledJobRegistry

redis = redis.Redis()
queue = Queue(connection=redis)
started = StartedJobRegistry('default', connection=redis)
schedu = ScheduledJobRegistry('default', connection=redis)

queued_jobs = started.get_queue().get_job_ids()
print(queued_jobs)
for id in queued_jobs:
    print(id)


for job_id in queued_jobs:
    started.remove(job_id, delete_job=True)
# This is how to remove a job from a registry
# for job_id in registry.get_job_ids():
#     registry.remove(job_id)
#     print('12')

# # If you want to remove a job from a registry AND delete the job,
# # use `delete_job=True`
# for job_id in registry.get_job_ids():
#     registry.remove(job_id, delete_job=True)
#     print('x')

print(queued_jobs)