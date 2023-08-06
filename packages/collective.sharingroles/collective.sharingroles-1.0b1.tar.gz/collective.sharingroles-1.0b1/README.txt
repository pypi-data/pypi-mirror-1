Introduction
============

This package provides services for managing the roles shown on the 'Sharing'
page in Plone.

Specifically, it provides a GenericSetup handler to export/import the
available roles. The file should be called `sharing.xml`, and have the
following format::

    <sharing>
        <role
            id="CopyEditor"
            title="Can edit copy"
            permission="Manage portal"
            />
    <sharing>
    
The id must match a role already installed (e.g. with rolemap.xml). The title
is the name to be shown on the sharing page. The required_permission is
optional. If given, the user must have this permission to be allowed to manage
the particular role.
