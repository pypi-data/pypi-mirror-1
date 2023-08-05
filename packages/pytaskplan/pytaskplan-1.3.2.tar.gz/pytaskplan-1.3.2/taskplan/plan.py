import time, csv, sys

from taskplan.task import Task, Event
from taskplan.person import Person
from taskplan.milestone import Milestones
from taskplan.gantt import Gantt

class Planner(Gantt):
    def __init__(self, tasks_file, people_file, done_file):
        # load the data
        self.events = {}
        self.loadTasks(tasks_file)
        self.loadPeople(people_file)
        self.loadDone(done_file)
        self.milestones = Milestones()

    def loadTasks(self, file):
        ''' load tasks from a CSV file '''
        labels = 'id group task skill effort depends'.split()

        self.tasks = {}
        first = 1
        for task in csv.reader(open(file)):
            task = [x.strip() for x in task]
            if first:
                assert task == labels, '%r != %r'%(task, labels)
                first = 0
                continue

            # skip blank lines
            if not task or len(task) == 1:
                continue

            id = int(task[0])
            if self.tasks.has_key(id):
                raise KeyErorr, 'duplicate key %d'%id
            d = {}
            self.tasks[id] = Task(d)
            for i in range(6):
                if i in (0, 4):
                    d[labels[i]] = int(task[i])
                elif i == 5:
                    d[labels[i]] = [int(x) for x in task[i].split(':') if x]
                else:
                    d[labels[i]] = task[i]

        # xref the dependencies
        for task in self.tasks.values():
            for dep in task['depends']:
                self.tasks[dep].blocks.append(task)
                task.deps.append(self.tasks[dep])

    def loadPeople(self, file):
        ''' load tasks from a CSV file '''
        labels = 'name skills colour'.split()

        self.people = []
        first = 1
        for person in csv.reader(open(file)):
            person = [x.strip() for x in person]
            if first:
                assert person == labels, '%r != %r'%(person, labels)
                first = 0
                continue
            # skip blank lines
            if not person or len(person) == 1:
                continue

            name, skills, colour = person
            skills = skills.split(':')
            self.people.append(Person(name, skills, colour))

    def loadDone(self, file):
        labels = 'week day numdays who activity'.split()

        pd = {}
        for person in self.people:
            pd[person.name] = person

        first = 1
        for done in csv.reader(open(file)):
            done = [x.strip() for x in done]
            if first:
                assert done == labels, '%r != %r'%(done, labels)
                first = 0
                continue
            # skip blank lines
            if not done or len(done) == 1:
                continue

            week, day, numdays, who, activity = done
            week, day, numdays = [int(x) for x in week, day, numdays]

            # figure the activity
            if activity.startswith('task:'):
                activity = self.tasks[int(activity[5:])]
            else:
                activity = self.getEvent(activity)

            pd[who].preset(week, activity, days=range(day, day+numdays))
            if not isinstance(activity, Task):
                continue

            # It's a task
            activity.done += numdays
            if not activity.isCompleted():
                # hard-code to this person so it's not reallocated to
                # someone else
                activity.task['skill'] = who
                continue

            # if it's completed, mark the end date
            activity.allocated = 1
            if day+numdays < 4:
                activity.end = (week, day+numdays)
            else:
                activity.end = (week+1, 0)

    def getEvent(self, label):
        if not self.events.has_key(label):
            self.events[label] = Event(name=label)
        return self.events[label]


    def plan(self):
        # now fill in the gaps
        while 1:
            change = 0
            for task in self.tasks.values():
                if task.allocated or task.isCompleted():
                    continue
                change = self.planTask(task) or change
            if not change:
                break

        for task in self.tasks.values():
            if not task.allocated:
                print 'NOT ALLOCATED', task['group'], task['task']

    def planTask(self, task):
        # can't continue if a dep isn't satisfied
        ends = []
        for dep in task.deps:
            if not dep.allocated:
                return 0
            ends.append(dep.end)

        # figure the earliest start date from deps
        ends.sort()
        if not ends:
            start_week, start_day = (0,0)
        else:
            start_week, start_day = ends[-1]

        # zero-effort task (ie. a milestone)?
        if not task['effort']:
            task.end = (start_week, start_day)
            task.allocated = 1
            self.milestones.add(task)
            return 1

        # find first available person
        free = []
        for person in self.people:
            if (task['skill'] == person.name or
                    task['skill'] in person.skills):
                week, day = person.estimateTaskEnd(start_week,
                    start_day, task['effort'])
                free.append((week, day, len(person.skills), person))
        free.sort()
        person = free[0][3]
        week, day = person.findFreeWeek(start_week, start_day)
        person.doTask(task, week, day)
        return 1


    def determineTaskPaths(self):
        def pathsToTask(task):
            paths = []
            if not task.deps:
                return [[task['id']]]
            for dep in task.deps:
                for path in pathsToTask(dep):
                    paths.append(path + [task['id']])
            return paths

        l = []
        for task in self.tasks.values():
            l.extend(pathsToTask(task))

        l.sort(lambda x,y:cmp(len(x), len(y)))
        return l


    def dumpTasks(self, f=sys.stdout):
        print >>f, '<table border cellspacing=0 cellpadding=2>'
        print >>f, '<tr><th>ID</th><th>Group</th><th>Task</th><th>Skill</th><th>Effort</th><th>Depends</th></tr>'
        taskids = self.tasks.keys()
        taskids.sort()
        for taskid in taskids:
            print >>f, '<tr><td>%(id)d</td><td>%(group)s</td><td>%(task)s</td>'\
                '<td>%(skill)s</td><td>%(effort)d</td><td>%(depends)s</td>'\
                '</tr>'%self.tasks[taskid]
        print >>f, '</table>'


    def dumpPlan(self, start=time.time(), f=sys.stdout):
        ONE_WEEK = 7*24*60*60
        week = 0
        all = self.people + [self.milestones]
        print >>f, '''<style type="text/css">
td,th {vertical-align: top; white-space: pre; empty-cell: show}
.tip {border:solid 1px #666666; padding:1px; position:absolute; z-index:100;
      visibility:hidden; color:#333333; top:20px; left:90px;
      background-color:#ffffcc; layer-background-color:#ffffcc;}
a.tiptarget {color: black}
a.tiptarget:hover {color: black; text-decoration: none}
</style>
<script language="javascript">
// Extended Tooltip Javascript
// copyright 9th August 2002, 3rd July 2005
// by Stephen Chapman, Felgall Pty Ltd
// permission is granted to use this javascript provided that the below code is not altered
var DH = 0;var an = 0;var al = 0;var ai = 0;if (document.getElementById) {ai = 1; DH = 1;}else {if (document.all) {al = 1; DH = 1;} else { browserVersion = parseInt(navigator.appVersion); if ((navigator.appName.indexOf('Netscape') != -1) && (browserVersion == 4)) {an = 1; DH = 1;}}} function fd(oi, wS) {if (ai) return wS ? document.getElementById(oi).style:document.getElementById(oi); if (al) return wS ? document.all[oi].style: document.all[oi]; if (an) return document.layers[oi];}
function pw() {return window.innerWidth != null? window.innerWidth: document.body.clientWidth != null? document.body.clientWidth:null;}
function mouseX(evt) {if (evt.pageX) return evt.pageX; else if (evt.clientX)return evt.clientX + (document.documentElement.scrollLeft ?  document.documentElement.scrollLeft : document.body.scrollLeft); else return null;}
function mouseY(evt) {if (evt.pageY) return evt.pageY; else if (evt.clientY)return evt.clientY + (document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop); else return null;}
function popUp(evt,oi) {if (DH) {var wp = pw(); ds = fd(oi,1); dm = fd(oi,0); st = ds.visibility; if (dm.offsetWidth) ew = dm.offsetWidth; else if (dm.clip.width) ew = dm.clip.width; if (st == "visible" || st == "show") { ds.visibility = "hidden"; } else {tv = mouseY(evt) + 20; lv = mouseX(evt) - (ew/4); if (lv < 2) lv = 2; else if (lv + ew > wp) lv -= ew/2; if (!an) {lv += 'px';tv += 'px';} ds.left = lv; ds.top = tv; ds.visibility = "visible";}}}
</script>
<table border=1 cellspacing=0 cellpadding=2>
<tr><th>Date</th><th>Day</th>'''
        for events in all:
            print >>f, '<th>%s</th>'%events.name
        print >>f, '</tr>'
        while 1:
            date = time.strftime('%d %b', time.localtime(start + week*ONE_WEEK))
            print >>f, '<tr><td><strong>%s</strong><br>(wk %s)</td>'%(date,
                week)
            print >>f, '<td>Mon\nTue\nWed\nThu\nFri</td>'
            got = 0
            for n, events in enumerate(all):
                if events.hasWeek(week):
                    print >>f, '<td>%s</td>'%events.getWeek(week).asHTML(n)
                    got = 1
                else:
                    print >>f, '<td></td>'
            print >>f, '</tr>'
            if not got:
                break
            week += 1
        print >>f, '</table>'


# vim: set filetype=python ts=4 sw=4 et si

