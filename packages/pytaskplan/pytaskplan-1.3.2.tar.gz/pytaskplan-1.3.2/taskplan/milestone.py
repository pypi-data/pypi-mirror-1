

class Milestone:
    def __init__(self, task):
        self.tasks = [task]

    def asHTML(self, uid):
        return '\n'.join(['%(task)s<br>'%task for task in self.tasks])

class Milestones:
    name = 'Milestones'
    def __init__(self):
        self.milestones = {}

    def hasWeek(self, week):
        return self.milestones.has_key(week)

    def getWeek(self, week):
        return self.milestones[week]

    def add(self, task):
        if self.milestones.has_key(task.end[0]):
            self.milestones[task.end[0]].tasks.append(task)
        else:
            self.milestones[task.end[0]] = Milestone(task)

