Checklists for Plone HRM
========================

With this package you can add checklists to an Employee.  There you
can keep track of things that need doing, like getting a copy of their
passport for your administration.


If you set a due date for a checklist item and tick the email
notification option, a reminder will also be sent.

N.B. The email notification system works by simply sending an email
for every checklist item that is due _today_ (and has the notification
option set). In other words, this package assumes that the
IHRMCheckEvent is fired only once a day, preferrably before working
hours. In other words: if the event is fired more than once a day, the
emails will be sent more than once.
