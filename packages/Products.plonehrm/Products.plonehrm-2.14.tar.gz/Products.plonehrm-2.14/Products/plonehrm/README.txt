Plone HRM
=========

Plone HRM is an open source Plone product designed to manage human
resources.

Functionalities (for end users):
--------------------------------

PloneHRM is formed around two major types of items: worklocations
and employees. You can create as many worklocations as you need and in
each of them, as many employees as you want without any limitation.
One goal of PloneHRM is to be easy to use, so almost all
functionalities are handled in employee folders and worklocation views.

When seeing the folder of an employee, you have access to several
widgets that help you maintain your employee folder.

Personal data:

- save all personal data about your employee (contact, birth date,
  portrait ...)

Notes:

- add notes about your employee

Tasks:

- create tasks for each employee
- set a due date for the task. The task will appear orange on the due
  date and red if the task has not been done after the due date
- get a notification by mail on the due date

Files:

- save files about your employee (correspondence, passport copies,
  vacations overview ...) 

Contracts:

- create contracts and change letters
- use templates to automatically generate the contract from
  the data of the employee
- manage which days an employee works on odd/even weeks and how many
  hours each day
- get notifications when a contract or a trial period is close to
  expire

Job performance interviews:

- use templates to generate the skeleton of your interview reports
- store improvements areas

Absences:

- create/close an employee absence
- manage percentage of presence/productivity during an absence
- have a history of the percentages evolution
- obtain the exact number of absence days from contract definition
- create interviews about re-integration after long absences
- add notes and files to an absence
- get notified when an employee is absent for a long period


The worklocation page offers six different overviews:

- the list of employees currently employed in a worklocation with
  their contact information
- the improvement area view lets you see all improvement areas defined
  with your employees during the last job interviews
- the absence view provides a year overview of the absences of your
  employees and allows you to export the list of absences for a given 
  period as a CSV file (compatible with Excel)
- the facebook view shows a facebook of your employees with a quick
  access to their folders
- the tasks view shows all tasks that are left to be done and allows
  to change the due date or mark them as done
- the inactive employee view allows you to access the folders of your
  former employees


Incoming features:
------------------

PloneHRM is still evolving and some new features are planned for the
coming months:

- new widget to manage employees vacations
- year/month/week overview of the vacations for a worklocation
- new widget to manage correspondence with employees
- new widget to manage education and courses of employees
- template system allowing to automatically generate forms for
  administrations


PloneHRM features (for integrators):
---------------------------------------------------

PloneHRM can be easily integrated in your Plone site. In your
buildout, add the following code::

  [buildout]
  ...
  eggs =
      Products.plonehrm
  versions = versions

  [versions]
  Products.plonehrm = 2.14
  plonehrm.absence = 1.5
  plonehrm.checklist = 1.3
  plonehrm.contracts = 2.6
  plonehrm.jobperformance = 1.3
  plonehrm.notes = 1.1
  plonehrm.notifications = 1.2
  plonehrm.personaldata = 2.0.1

In the next major release (3.0), PloneHRM will be a single package, so
you will not have to specify versions for each sub-package.

Once PloneHRM is installed in your Plone instance, you get the
possibility to add Worklocation objects inside any Plone folder
(except if you restricted addable types of course).

New configlets will also be added in your plone control panel:

- PloneHRM notifications allows you to set when notifications are sent
  by the system.
- absence evaluation templates let you define templates for interviews
  done during absences
- job performance templates do the same for job performance templates
- contract templates allow you to define templates for contracts and
  letters

You can simply customise all e-mail notifications sent by PloneHRM,
for example using HTML mails using your company logo. See the 'for
developers' section of this file for more explanation.

PloneHRM is a modular system and you can decide to restrict access to
your users by using custom roles and permissions (see the 'for
developers' for more details). You can hide a widget in the employees
views, show a widget as static widget (no possibility to add a new
task for example) or allow the full access to the widget.
For each widget, you can control how the user will access it.


PloneHRM features (for developers):
------------------------------------

PloneHRM defines several permissions to restrict user interface. Those
permissions are named 'plonehrm: ...'.

For each viewlet/widget in the Employee view, you have a permission
called 'plonehrm: view ... viewlet' that you can use to hide the
viewlet to certain roles. The 'plonehrm: manage ...' is used to grant
access to the viewlets functionalities.

Content types also have custom permissions that you can use to
restrict access, like 'plonehrm: Add Contract' for example can be used
to (un)allow a user to add new contracts.

If you want to change the look of notification mails, you have to
override the base_email.pt template in the skin folder. This template
defines three macros that are used to render content of the mails:

- ``plonehrm_mail`` defines the content of the mail.
- ``plonehrm_p`` defines a text block (can be rendered as a 'p' tag in an
  html mail)
- ``plonehrm_link`` defines how a link should be rendered.


Licensing and releases:
-----------------------

Plone HRM is released under the GNU Public Licence (see
'docs/LICENCE.GPL'). Still, the SVN repository is not a public
repository, as we (Zest software) want to keep the newest features for
our customers. There will still be releases on Pypi
(http://pypi.python.org/pypi/Products.plonehrm/) but the eggs
publication will be delayed compared to the internal releases (for
example, the 3.0 release egg will be publicly available when the
internal 4.0 release will occur).

If you are interested in contributing to the project, please contact
the product manager (v.pretre at zestsoftware dot nl) to get an access
to the SVN repository. Contributors will be able to use the latest
releases.

The old public releases (see below) will still be accessible on Pypi
and sources will be accessible on the Plone collective SVN repository.
The list below provides, for each PloneHRM product, the last public
release and the SVN repository access::

  Products.ploneHRM        2.14   http://svn.plone.org/svn/collective/Products.plonehrm/
  plonehrm.absence         1.5    http://svn.plone.org/svn/collective/plonehrm.absence/
  plonehrm.checklist       1.3    http://svn.plone.org/svn/collective/plonehrm.checklist/
  plonehrm.contracts       2.6    http://svn.plone.org/svn/collective/plonehrm.contracts/
  plonehrm.jobperformance  1.3    http://svn.plone.org/svn/collective/plonehrm.jobperformance/
  plonehrm.notes           1.1    http://svn.plone.org/svn/collective/plonehrm.notes/
  plonehrm.notifications   1.2    http://svn.plone.org/svn/collective/plonehrm.notifications/
  plonehrm.personaldata    2.0.1  http://svn.plone.org/svn/collective/plonehrm.personaldata/
  plonehrm/dutch           1.3.1  http://svn.plone.org/svn/collective/plonehrm.dutch/
