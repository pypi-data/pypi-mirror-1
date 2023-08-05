A simple task planner capable of:

- resource allocation
- interruptions (holidays, etc)
- HTML plan generation
- HTML gantt chart generation

Basic Instructions
==================

1. Edit tasks.csv, people.csv and done.csv to include all your information.
   See the section below on input formats for help.

2. Run the script in the directory that has the csv files.

   ``python pytaskplan -t``
     Generates an HTML dump of the task list.

   ``python pytaskplan -p``
     Plans the tasks and generates a nice table of the tasks allocated by week
     and person.
    
   ``python pytaskplan -g``
     Plan the tasks and generate a pretty Gantt chart of their allocations
     over time and to people.

   See ``python pytaskplan -h`` for more usage help and info.

   The script will generate an HTML file for each of the output types
   (task.html, plan.html and gantt.html).


Input Formats
=============

All input files are CSV format. Commas separate fields. If you need to put
a comma in a field, then surround the field in "double quotes".

Blank lines are ignored.

The actual results of running the samples below are available as a `task
list`_, `task plan`_ and `gantt chart`_.

.. _`task list`: tasks.html
.. _`task plan`: plan.html
.. _`gantt chart`: gantt.html

tasks.csv
"""""""""
Each line contains:

id
  Unique number for the task.
group
  Label that groups a number of tasks - is added to the task label in
  displays. Helps me organise task input. Not used for anything else yet.
task
  Label for the task.
effort
  Number of days this task will take. An entry with 0 effort is regarded as
  a milestone. These are displayed in a special column in the plan, and may
  be used as dependencies.
skill
  Either a skill or a person who is required to perform the task
depends
  A colon ":" separated list of task ids that must be performed before this
  task may be performed.

For example (a sample from one of my projects)::

 id,  group,     task,                      skill,   effort, depends
 1,   Core,      Outline requirements,      Rachel,  5,
 2,   Core,      Basic functional spec,     Rachel,  10,     1

 10,  Database,  Define data model,         dba,     5,      2
 11,  Database,  Plan database,             dba,     5,      10
 12,  Database,  Implement store 1,         dba,     5,      11

 20,  Logic,     Component 1,               dev,     5,      2
 21,  Logic,     Component 2,               dev,     7,      20
 22,  Logic,     Component 3,               dev,     10,     20
 23,  Logic,     Component 4,               dev,     5,      21

 40,  Frontend,  Design interface,          web,     5,      2
 41,  Frontend,  Component 1,               web,     5,      40:20
 42,  Frontend,  Component 2,               web,     5,      40:21
 43,  Frontend,  Component 3,               web,     5,      40:22
 44,  Frontend,  Component 4,               web,     5,      40:23

 50,  Milestone, Milestone 1,               ,        0,      12:23:44

 14,  Database,  Optmisation,               dba,     5,      50

 24,  Support,   Supporting code,           dev,     10,     50

 45,  Frontend,  User walkthrough,          web,     15,     50
 46,  Frontend,  Rework based on feedback,  web,     10,     45


people.csv
""""""""""
Each line contains:

name
  The name of the person
skills
  A colon ":" separated list of skills the person has. Same labels as in
  the tasks CSV.
colour
  An HTML-compatible colour specification. It could be a colour name, or a
  hex RGB colour spec (ie. #FFF for white, #F00 for red, ...)

For example::

 name,    skills,      colour
 Fred,    web:dev,     red
 Rachel,  web:dba:dev, green
 Nicole,  dba,         blue


done.csv
""""""""
Contains a list of actual activities that have taken place (or are expected
to take place) during the plan. Each line contains:

week
  The week number that the activity took place. 
day
  The first day of the activity.
numdays
  The number of days the activity took.
who
  The name of the person performing the activity.
activity
  The actual activity that took place. Can take one of two forms. The first
  is "task:N" where N is a task id. This anchors at least part of the task
  to the day(s) specified (and to the person specified).
  
  The other form is an arbitrary label like "Public Holday" or "Gone
  Fishing".  This is used to indicate that the person is not available for
  scheduling during the day(s) indicated.

For exmaple (one week into our project)::

 week, day,numdays,who,     activity
  1,   0,  1,      Rachel,  Public Holiday
  1,   0,  1,      Nicole,  Public Holiday
  1,   0,  1,      Fred,    Public Holiday

  5,   2,  3,      Rachel,  Zope 3 Sprint
  5,   2,  3,      Fred,    Zope 3 Sprint

  4,   0,  5,      Nicole,  Leave
  5,   0,  5,      Nicole,  Leave

  4,   0,  5,      Fred,    Leave



License
=======

Copyright (c) 2004 Richard Jones (richard at mechanicalcat)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

