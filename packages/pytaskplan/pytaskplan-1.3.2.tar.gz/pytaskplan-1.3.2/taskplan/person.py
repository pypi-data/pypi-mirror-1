''' Define resources available for planning.

    Basic resources are People, who have Weeks/days to work on.

    Also defined here are Milestones, which look like People so they may be
    displayed in the same output.
'''

import cgi

from task import Task

class Person:
    def __init__(self, name, skills, colour):
        self.name = name
        self.skills = skills
        self.colour = colour
        self.weeks = {}          # week: (num days, [(task, num days),])

    def hasWeek(self, week):
        return self.weeks.has_key(week)
    def getWeek(self, week):
        return self.weeks[week]

    def __repr__(self):
        return '<Person %s>'%self.name

    def preset(self, week, activity, days=None):
        w = self.weeks.setdefault(week, Week(week))
        w.preset(activity, days)

    def findFreeWeek(self, start_week, start_day):
        ' Find the first day this person is free '
        week = start_week
        while 1:
            days = self.weeks.get(week, Week(week))
            day = 0
            if week == start_week:
                day = start_day
            day = days.nextFree(day)
            if day is not None:
                return (week, day)
            week += 1

    def estimateTaskEnd(self, start_week, start_day, duration):
        ' Determine when this person would finish a task '
        week, day = self.findFreeWeek(start_week, start_day)
        days = self.weeks.get(week, Week(week))
        while duration>0:
            nextfree = days.nextFree(day)
            if nextfree is not None:
                duration -= days.freeDays(nextfree)
            week += 1
            day = 0
            days = self.weeks.get(week, Week(week))
        return (week, day)

    def doTask(self, task, start_week, start_day):
        ''' Have the person do the task at their earliest time, limited by
            start_week and start_day '''
        week = start_week
        dur = task['effort'] - task.done
        task.person = self
        days = self.weeks.setdefault(week, Week(week))
        while 1:
            if week == start_week:
                dur = days.takeFree(task, dur, start_day)
            else:
                dur = days.takeFree(task, dur)

            if not dur:
                task.allocated = 1
                break
            week += 1
            days = self.weeks.setdefault(week, Week(week))

class Week:
    def __init__(self, week):
        self.week = week
        self.days = [None,None,None,None,None]

    def __repr__(self):
        return '<Week %d %r>'%(self.week, self.days)

    def __str__(self):
        l = self.taskSummary()
        return '\n'.join(['%d: %s %s'%e for e in l])

    def preset(self, info, indexes=None):
        if indexes is None:
            indexes = range(5)
        for i in indexes:
            self.days[i] = info

    def tdCells(self):
        l = self.taskSummary()
        return '\n'.join(['<td>%d</td><td>%s %s</td>'%e for e in l])

    def asHTML(self, uid):
        uid = '%s-%s'%(self.week, uid)
        l = []
        old = None
        n = 0
        for i in range(5):
            task = self.days[i]
            title = ''
            if task is None:
                label = '&nbsp;'
            elif task.label() == old:
                l.append('...')
            else:
                old = label = task.label()
                if len(label) > 30:
                    title = cgi.escape(label)
                    label = label[:27] + ' ...'
                    n += 1
                label = cgi.escape(label)
                if title:
                    l.append('<div id="t%s%s" class="tip">%s</div>'%(uid,
                        n, title))
                    l.append('''<a class="tiptarget" href="#"
                        onmouseout="popUp(event,'t%s%s')"
                        onmouseover="popUp(event,'t%s%s')"
                        onclick="return false">%s</a>'''%(uid, n, uid, n,
                        label))
                else:
                    l.append(label)
        return '\n'.join(l)

    def taskSummary(self):
        current = None
        l = []
        n = 0
        for i in range(5):
            if self.days[i] is None:
                n += 1
                continue
            if current is None:
                current = (self.days[i], 1)
            elif current[0] != self.days[i]:
                task = current[0]
                if task.isCompleted():
                    l.append(('-', task['group'], task['task']))
                else:
                    l.append((current[1], task['group'], task['task']))
                current = (self.days[i], 1)
            else:
                current = (self.days[i], current[1]+1)
        task = current[0]
        if isinstance(task, Task) and task.isCompleted():
            l.append(('-', task['group'], task['task']))
        else:
            l.append((current[1], task['group'], task['task']))
        if n:
            l.append((n, 'Other', 'UNUSED'))
        return l

    def numFree(self):
        return len([day for day in self.days if not day])

    def nextFree(self, start):
        ' figure the next free day, possibly starting on a given day '
        for i in range(start, 5):
            if not self.days[i]:
                return i
        return None

    def freeDays(self, start):
        ' figure the number of free days, possibly starting on a given day '
        n = 0
        for i in range(start,5):
            if not self.days[i]:
                n += 1
        return n

    def takeFree(self, task, num, start=0):
        for i in range(start, 5):
            if self.days[i]:
                continue
            self.days[i] = task
            task.days.append((self.week, i))
            if i < 4:
                task.end = (self.week, i+1)
            else:
                task.end = (self.week+1, 0)
            num -= 1
            if not num:
                break
        return num

