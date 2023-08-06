Introduction
============

An Archetypes field that manages local roles. It can be used to assign 
specific local roles through the edit form.

Usage
-----

An example field definition

    ... RoleField(
    ...     'responsible,
    ...     role = 'Owner',
    ...     widget = SelectionWidget(
    ...         label = 'Responsible',
    ...     ),
    ... ),

The available parameters are:

    - 'role': the managed role that will be assigned to users;

    - 'target_expression': An expression returning the target object 
    where local roles should be assigned. If None (default), context 
    will be used as target.
    
    - 'allow_protected_roles': Allow the user to change protected 
    roles for himself. Default is False.

    - 'protected_roles': Roles that a user shouldn't be able to 
    change for himself, if 'allow_protected_roles' is True. 
    Default is ('Manager', 'Owner').

    - 'filter_groups': Filter users/groups by group. If None, no 
    filter is made. Only used if vocabulary is None and so the 
    default vocabulary is used.

    - 'principals': Possible values are 'users' (default), 'groups' 
    and 'all'. Only used if 'vocabulary' is None and so the default 
    vocabulary is used.


Read archetypes/rolefield/tests/rolefield.text for more details.


Installation
------------

Add archetypes.rolefield to your buildout configuration. Install the 
product in Plone through the Add-on products control panel.


Credits
-------

Ricardo Alves <rsa at eurotux dot com>

Eurotux Development Team <udp at eurotux dot com>


License
-------

Read docs/LICENSE.GPL
