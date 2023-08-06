Introduction
============

This package provides a new portlet for Plone 3 called "Contribute content".
It can be configured with some rich text, a folder and a list of addable
types. It is also possible to specify that the portlet should always work on
the folder where it is being viewed (note that on the dashboard, that will
be the Plone site root!).

The portlet will display either an "Add <type name>" button, if there is a
single addable type, or a drop-down list, if more than one type is available.
Note that the list of available types will depend on the current user's
permissions in the designated target folder. If no types are addable, the
portlet will be hidden.

Hint: This portlet works well together with collective.groupdashboard. Set up
a dashboard for each group.

The ability to add a new "Contribute content" portlet depends on the
"Contribute Content Portlet: Add portlet" permission. By default, this is
given to managers only.

(Note that until Plone 3.3, there was a bug in the portlet management code
that would show portlets that the user did not have permission to view in the
"add portlet" list. See https://dev.plone.org/plone/ticket/8403).