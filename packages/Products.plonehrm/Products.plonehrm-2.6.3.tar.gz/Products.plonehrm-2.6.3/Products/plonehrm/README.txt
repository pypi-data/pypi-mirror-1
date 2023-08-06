Plone HRM basic product
=======================

`plonehrm` is a product that aims to be an extensible basis for simple
HRM applications. Small firms, possibly divided into a couple of
worklocations or other business units. Each with a couple of
employees.

The actual functionality like address data, contracts, financial
information and so must be provided by separate so-called **employee
modules**.

It runs on Plone 3.0.


What plonehrm provides
----------------------

- The basic content types "worklocation" and "employee".

- An interface to which employee modules must conform.

- The content types have the capability to visualise themselves using
  the available employee modules.

- A portal_tool you can use: to register employee modules; to get a
  list of those employee modules; to get a list of all employees.


Upgrade information
-------------------

Between version 1.0 and 2.0 the plonehrm.personaldata module was
merged into Products.plonehrm.  You need to run some upgrade steps for
this.  With Plone 3.3 you can do this from the Add/Remove products
panel.  In earlier Plone versions, go to the Zope Management
interface, then portal_setup, then the Upgrades tab, choose the
Products.plonehrm:default profile and run the upgrade steps.
