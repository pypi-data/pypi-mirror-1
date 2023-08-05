__rcs_id__ = '$Id'
__version__ = '$Revision: 1.4 $'[11:-2]

import csv

class Task:
    def __init__(self, task=None):
        self.task = task
        self.allocated = 0
        self.done = 0           # amount of days actually spent on task
        self.blocks = []
        self.deps = []
        self.days = []          # days that this task is active on
        self.end = None         # (week, day) of day _after_ this task

    def isMilestone(self):
        return self.task['group'] == 'Milestone'

    def isCompleted(self):
        return self.done >= self['effort'] and not self.isMilestone()

    def __repr__(self):
        return '<Task %s 0x%x>'%(self.task['id'], id(self))

    def __getitem__(self, key):
        return self.task[key]

    def label(self):
        return '%s %s'%(self.task['group'], self.task['task'])

    def fullDepList(self, loop=None):
        if loop is None:
            loop = []
        if self['id'] in loop:
            raise ValueError, loop
        loop.append(self['id'])

        l = []
        for node in self.deps:
            if node.deps:
                for r in node.fullDepList(loop):
                    d = [node['id']]
                    d.extend(r)
                    l.append(d)
            else:
                l.append([node['id']])
        loop.remove(self['id'])
        return l

class Event:
    def __init__(self, name):
        self.name = name
        self.allocated = 1

    def isMilestone(self):
        return self.task['group'] == 'Milestone'

    def isCompleted(self):
        return 0

    def __getitem__(self, key):
        if key == 'task':
            return self.name

    def label(self):
        return 'Event %s'%self.name

def taskLoader(file):
    ''' load tasks from a CSV file '''
    labels = ('id','group','task','skill','effort','depends')

    p = csv.parser()
    tasks = {}
    first = 1
    for line in open(file):
        task = p.parse(line)
        if not task:
            continue
        if first:
            assert task == labels, '%r != %r'%(data, labels)
            first = 0
            continue

        if tasks.has_key(task[0]):
            raise KeyErorr, 'duplicate key %d'%task[0]
        d = {}
        tasks[task[0]] = Task(d)
        for i in range(6):
            d[labels[i]] = task[i]

    # xref the dependencies
    for task in tasks.values():
        for dep in task['depends']:
            tasks[dep].blocks.append(task)
            task.deps.append(tasks[dep])
    return tasks

if __name__ == '__main__':
    print '<table border cellspacing=0 cellpadding=2>'
    print '<tr><th>ID</th><th>Group</th><th>Task</th><th>Skill</th><th>Effort</th><th>Depends</th></tr>'
    taskids = tasks.keys()
    taskids.sort()
    for taskid in taskids:
        print '<tr><td>%(id)d</td><td>%(group)s</td><td>%(task)s</td>'\
            '<td>%(skill)s</td><td>%(effort)d</td><td>%(depends)s</td>'\
            '</tr>'%tasks[taskid]
    print '</table>'

# vim: set filetype=python ts=4 sw=4 et si

