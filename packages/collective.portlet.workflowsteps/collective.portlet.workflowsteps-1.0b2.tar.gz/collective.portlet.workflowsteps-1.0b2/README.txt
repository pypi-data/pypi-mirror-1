Introduction
============

This package provides a new portlet for Plone 3 called "Workflow steps". It
can be configured to show:

  * A custom header
  * Some lead-in rich text, if desired
  * The state of the current object, including that state's full description
  * All available transitions, optionally with their full descriptions

State and transition descriptions are rendered as HTML. Furthermore, the
following special variables may be used.

  ${portal_url} -- The url of the portal (or navigation) root
  ${object_url} -- The url of the current object
  ${folder_url} -- The url of the current folder

The idea is to make it possible to present a list of "next steps" as part of
the workflow, including links to edit forms and the like.