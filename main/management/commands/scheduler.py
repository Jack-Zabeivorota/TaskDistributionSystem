from typing import Iterator
import time
import heapq
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Task, Worker


class WorkerWrap:
    def __init__(self, worker: Worker):
        self.worker = worker
        self.tasks_count = worker.tasks_count
    
    def __lt__(self, other: Worker):
        return self.tasks_count < other.tasks_count

    def __gt__(self, other: Worker):
        return self.tasks_count > other.tasks_count

    def __eq__(self, other: Worker):
        return self.tasks_count == other.tasks_count

class Command(BaseCommand):
    def _get_workers_for_tasks(self, tasks_len: int, min_workers: int = 2, keep_in_queue: int = 10) -> Iterator[Worker]:
        '''
        Get the required number of workers to perform tasks from the queue
        (first those already working are taken, then those free)
        Returns at least `min_workers` workers if they are in the DB
        '''

        query = '''
            SELECT name, tasks_count, max_tasks
            FROM (
                SELECT
                    name, tasks_count, max_tasks,
                    max_tasks - tasks_count AS free_tasks,
                    ROW_NUMBER() OVER (ORDER BY tasks_count DESC) AS row_number,
                    COALESCE(
                        SUM(max_tasks - tasks_count) OVER
		                (ORDER BY tasks_count DESC ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING),
                    0) AS total_free_tasks
                FROM main_worker
                ORDER BY tasks_count DESC
            )
            WHERE free_tasks > 0 AND (tasks_count > 0 OR (row_number <= %s OR total_free_tasks < %s))
        '''

        return Worker.objects.raw(query, [min_workers, tasks_len - keep_in_queue])

    def _task(self):
        print('START CHECING')

        tasks = list(Task.objects
                 .filter(status=Task.REVERSE_STATUS_MAP['pending'], worker__isnull=True)
                 .order_by('priority'))

        print('TASKS:', len(tasks))

        if not tasks:
            return
            
        workers = self._get_workers_for_tasks(len(tasks))

        print('SELECTED WORKERS:', len(workers))

        if not workers:
            return

        workers_heap = [WorkerWrap(worker) for worker in workers]
        heapq.heapify(workers_heap)

        i = 0

        while i < len(tasks):
            root = workers_heap[0]

            if root.tasks_count == float('inf'):
                break

            tasks[i].worker = root.worker
            root.worker.tasks_count += 1

            if root.worker.tasks_count < root.worker.max_tasks:
                root.tasks_count += 1
            else:
                root.tasks_count = float('inf')

            heapq.heapreplace(workers_heap, root)
                    
            i += 1
                
        with transaction.atomic():
            Worker.objects.bulk_update(workers, ['tasks_count'])
            Task.objects.bulk_update(tasks[:i+1], ['worker'])
        
        print('ASSIGNED TASKS:', i+1)
        print('END CHECING\n')

    def handle(self, *args, **kwargs):
        while True:
            self._task()
            time.sleep(10)