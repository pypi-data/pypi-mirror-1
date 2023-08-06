=============
WorkflowField 
=============

This product provides an Archetypes field to do workflow transitions on save
of an form.


Usage
=====
  
1. Place it as usual in your Products directory. 

2. Add this line to your custom Archetype to import the fields::
    
 from Products.WorkflowField import WorkflowField

3. In your schema, add fields like this::
    
 BaseSchema + Schema((
     WorkflowField('oneField'),
 ))


Issues
======

If the transition applied happens to remove permission 'Modify portal
content' from the user performing the edit, the field must be at the end of 
the schema, so the other mutators won't fail after the transition is applied.

Further Information
===================

Visit `plone.org/products/workflowfield <http://plone.org/products/workflowfield>`_ 
for releases, documentation, bug-reports, etc.

Source code lives at 
`svn.plone.org <http://svn.plone.org/svn/archetypes/MoreFieldsAndWidgets/WorkflowField>`_

Contributors
============

    - Jens Klein <jens@bluedynamics.com>

    - Ricardo Alves <rsa@eurotux.com>

Copyright
=========  
    
Originaly written by Jens Klein <jens@bluedynamics.com>
  
(C) 2008, BlueDynamics Alliance, Klein & Partner KEG, Austria

This code is under GPL 2 or later.
