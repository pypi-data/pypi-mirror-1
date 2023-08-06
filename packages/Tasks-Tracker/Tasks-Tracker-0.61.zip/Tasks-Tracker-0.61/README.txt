Task-Tracker -- A simple command line project task tracking tool
https://launchpad.net/tasks-tracker
Developed by: [Mohamed Diarra <moh@softwebia.com>]

Usage: tasks: [-n TASK] 

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -R, --recursive       run commands recursively in subfolders

  Setup commands:
    --init              initialize tasks in folder
    --un-init           un-initialize tasks for current folder (Removes .tasks
                        file).
    --reset             initialize new tasks in folder, loses all previous
                        tasks
    --empty-trash       permanently delete tasks in trash

  Basic tasks commands:
    -n ADD, --add=ADD   add a new task
    -c, --completed     set a task as completed
    -d, --delete        remove a task
    -a, --active        set a task as active

  List commands:
    -i, --indexed       show active tasks with index
    -C, --show-completed
                        show only completed tasks
    -D, --show-deleted  show trashed tasks
    -A, --show-all      show all tasks (active, completed and trashed)