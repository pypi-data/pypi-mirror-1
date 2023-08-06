"""Tasks modules with functions to do tasks operations"""

__copyright__ = """
    This file is part of Tasks-Tracker.

    Tasks-Tracker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Tasks-Tracker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tasks-Tracker.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os
from datetime import datetime
from configobj import ConfigObj

TASK_FILE_NAME = '.tasks'
TIME_FORMAT = "%a, %d %b %Y at %H:%M:%S"

STATUS_ACTIVE = ' '
STATUS_COMPLETED = '+'
STATUS_TRASHED = '-'

STATUS_CONVERT_MAP = {
    'Active': STATUS_ACTIVE,
    'Completed': STATUS_COMPLETED,
    'Trashed': STATUS_TRASHED
}

filepath = lambda: '%s' % (TASK_FILE_NAME)


class Task(object):
    """One task"""
    def __init__(self, desc, time=datetime.now(), status=STATUS_ACTIVE):
        self._time = time
        self._status = status
        self.desc = desc
        
    @property
    def time(self):
        return self._time
    
    @property
    def status(self):
        if self.active:
            return 'Active'
        if self.completed:
            return 'Completed'
        if self.trashed:
            return 'Trashed'
        
    @property
    def active(self):
        return self._status == STATUS_ACTIVE
    
    @property
    def completed(self):
        return self._status == STATUS_COMPLETED
    
    @property
    def trashed(self):
        return self._status == STATUS_TRASHED
    
    def mark_as_active(self):
        self._status = STATUS_ACTIVE
    
    def mark_as_completed(self):
        self._status = STATUS_COMPLETED
    
    def move_to_trash(self):
        self._status = STATUS_TRASHED

    def restore_from_trash(self):
        self._status = STATUS_ACTIVE
    
    def __str__(self):
        task_str = '%s [%s] %s' % (self._status, self.time.strftime(TIME_FORMAT), self.desc)
        return task_str

    __repr__ = __str__
    

def initialize():
    save_all_tasks([])
    

def un_initialize():
    os.remove(TASK_FILE_NAME)
    

def is_initialized():
    return os.path.lexists(filepath())


def get_all_tasks():
    return get_tasks_from_file(filepath())


def get_active_tasks():
    all_tasks = get_all_tasks()
    return get_actives(all_tasks)


def get_completed_tasks():
    all_tasks = get_all_tasks()
    return get_completed(all_tasks)


def get_trashed_tasks():
    all_tasks = get_all_tasks()
    return get_trashed(all_tasks)
    

def get_actives(all_tasks):
    return [ task for task in all_tasks if task.active ]


def get_completed(all_tasks):
    return [ task for task in all_tasks if task.completed ]


def get_trashed(all_tasks):
    return [ task for task in all_tasks if task.trashed ]


def save_all_tasks(all_tasks):
    sorted_all_tasks = get_actives(all_tasks)
    sorted_all_tasks.extend(get_completed(all_tasks))
    sorted_all_tasks.extend(get_trashed(all_tasks))
    
    save_tasks_to_file(sorted_all_tasks, filepath())


def add_task(task_description):
    all_tasks = get_all_tasks()
    all_tasks.append(Task(task_description))
    save_all_tasks(all_tasks)


def move_to_trash(task_index):
    all_tasks = get_all_tasks()
    all_tasks[task_index].move_to_trash()
    save_all_tasks(all_tasks)


def restore_from_trash(task_index):
    all_tasks = get_all_tasks()
    all_tasks[task_index].restore_from_trash()
    save_all_tasks(all_tasks)


def empty_trash():
    all_tasks = get_all_tasks()
    non_trashed_tasks = [ task for task in all_tasks if not task.trashed ]
    save_all_tasks(non_trashed_tasks)


def mark_as_completed(task_index):
    all_tasks = get_all_tasks()
    all_tasks[task_index].mark_as_completed()
    save_all_tasks(all_tasks)
    
    
def mark_as_active(task_index):
    all_tasks = get_all_tasks()
    all_tasks[task_index].mark_as_active()
    save_all_tasks(all_tasks)


def list_all_tasks(printer):
    list_tasks(printer, get_all_tasks(), with_index=True)

def list_active_tasks(printer, with_index=False):
    all_tasks = get_active_tasks()
    if not all_tasks:
        printer("There are no active tasks.")
        return
    
    printer("Current tasks: ")
    list_tasks(printer, all_tasks, with_index)
    
    
def list_completed_tasks(printer):
    all_completed_tasks = get_completed_tasks()
    if not all_completed_tasks:
        printer("No tasks have been completed.")
        return
    
    printer("Completed tasks: ")
    list_tasks(printer, all_completed_tasks)


def list_trashed_tasks(printer):
    all_tasks = get_trashed_tasks()
    if not all_tasks:
        printer("There are no tasks in the trash.")
        return
    
    printer("Tasks in trash: ")
    list_tasks(printer, all_tasks)
    
    
def list_tasks(printer, all_tasks, with_index=False):
    for index, task in enumerate(all_tasks):
        prev_task = all_tasks[index-1]
        curr_task = all_tasks[index]
        if prev_task.status != curr_task.status:
            printer("")
            printer('%s tasks: ' % curr_task.status)
            
        if with_index:
            printer('[%s] %s' % (index + 1, task))
        else:
            printer(task)


def save_tasks_to_file(all_tasks, filename):
    config = ConfigObj(infile=filename)
    config.clear()
    for index, task in enumerate(all_tasks):
        config[str(index)] = {'time': task.time.strftime(TIME_FORMAT), 'desc': task.desc, 'status': task.status}
    config.write()


def get_tasks_from_file(filename):
    all_tasks = []
    config = ConfigObj(infile=filename)

    for index, task in config.items():
        task_desc = task['desc']
        task_time = datetime.strptime(task['time'], TIME_FORMAT)
        task_status = STATUS_CONVERT_MAP[task['status']]

        all_tasks.append(Task(task_desc, task_time, task_status))
    
    return all_tasks