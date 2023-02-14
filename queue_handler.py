import redis
from rq import Queue, cancel_job
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry, CanceledJobRegistry
from rq.command import send_stop_job_command
from rq.job import Job
from rq.suspension import suspend, resume
import sqlite3
import file_handler

# Definieren der Queue über den Redis Server
r = redis.Redis()
q = Queue(connection=r)

# Funktion zum Auslesen der in der Queue laufenden Prozesse und der fertigen Prozesse aus der Datenbank
def queue_handler_function():
    # Überprüfen der Ordner der neuen und zu bearbeiteten Files
    if file_handler.check_first():
        # Die Funktion zum Verschieben von neuen zum edit Ordner in die Queue einbinden
        move_job = q.enqueue(file_handler.move_file_from_new_to_edit)
        # Die Funktion zum Checken der PDF File in die Queue einbinden, in Abhängigkeit ob move_job erfolgreich war
        check_job = q.enqueue(file_handler.check_file_info, depends_on=move_job)
        # Die Funktion zum Verschieben vom edit zum done Ordner, in Abhängigkeit ob check_job erfolgreich war
        finish_job = q.enqueue(file_handler.move_file_from_edit_to_finished, depends_on=check_job)

    # Auslesen sämliche Jobs in der Queue: Running, in Warteschleife, Fertige, Fehlgeschlagene und gecancelte Jobs
    registry_start = StartedJobRegistry('default', connection=r)
    running_jobs = registry_start.get_job_ids()
    queued_jobs = registry_start.get_queue().get_job_ids()
    registry_finished = FinishedJobRegistry('default', connection=r)
    finished_jobs = registry_finished.get_job_ids()
    registry_failed = FailedJobRegistry('default', connection=r)
    failed_jobs = registry_failed.get_job_ids()
    registry_canceled = CanceledJobRegistry('default', connection=r)
    canceled_jobs = registry_canceled.get_job_ids()
    tasks = []
    # Einfügen der laufenden Jobs in das Tasks Array
    for id in running_jobs:
        job = registry_start.get_queue().fetch_job(id)
        tasks.append({
            'id': id,
            'status': job.get_status(),
            'start': job.enqueued_at
        })
    # Einfügen der wartenden Jobs in das Tasks Array
    for id in queued_jobs:
        job = registry_start.get_queue().fetch_job(id)
        tasks.append({
            'id': id,
            'status': job.get_status(),
            'start': job.enqueued_at
        })   
    # Verbinden mit der Datenbank
    con = sqlite3.connect('jobs.db')
    cur = con.cursor()
    # Auslesen der fertigen Jobs aus der Queue, diese aus der Queue löschen und in die Datenbank einfügen
    for id in finished_jobs:
        job = registry_finished.get_queue().fetch_job(id)
        fin_jobs = []
        fin_jobs.append((
            id,
            job.get_status(),
            job.enqueued_at
        ))
        # Jobs in Datenbank einfügen
        cur.executemany('INSERT INTO finishedjobs VALUES (?, ?, ?)', fin_jobs)
        # Jobs aus Queue löschen
        registry_finished.remove(id)
        con.commit()
    # Jobs aus Datenbank wieder auslesen und in Tasks Array einfügen
    result = cur.execute('SELECT * FROM finishedjobs')
    for x in result.fetchall():
        tasks.append({
            'id': x[0],
            'status': x[1],
            'start': x[2]
        })
    # Einfügen der Failed Jobs in das Tasks Array
    for x in failed_jobs:
        alls = registry_failed.get_queue().fetch_job(x)
        tasks.append({
            'id': x,
            'status': alls.get_status(),
            'start': alls.enqueued_at
        })
    # Einfügen der Abgebrochenen Jobs in das Tasks Array
    for x in canceled_jobs:
        alls = registry_canceled.get_queue().fetch_job(x)
        if (alls):
            tasks.append({
                'id': x,
                'status': alls.get_status(),
                'start': alls.enqueued_at
            })  
    # Zurückgeben des Tasks Array
    return tasks


# Funktion zum Restarten der Queue
def restart_queue():
    con = sqlite3.connect('jobs.db')
    cur = con.cursor()
    cur.execute('UPDATE paused SET task = 1 WHERE id=1')
    con.commit()
    resume(q.connection)

# Funktion zum Pausieren der Queue
def pause_queue():
    con = sqlite3.connect('jobs.db')
    cur = con.cursor()
    cur.execute('UPDATE paused SET task = 0 WHERE id=1')
    con.commit()
    suspend(q.connection)

# Funktion um den Status der Queue zu überprüfen mit einem in der Datenbank gespeicherten Wert
def check_queueon():
    con = sqlite3.connect('jobs.db')
    cur = con.cursor()
    res = cur.execute('SELECT * FROM paused')
    for x in res.fetchall():
        queueon = x[1]
    return queueon

