Introduction
============

This package provides a complete Plone user interface for ``AdvancedQuery`` by
Dieter Maurer. It enables you to use a powerful language to search for
content. It also provides functionality to save parametrized and conditional
queries for later use (predefined queries). Look at the examples for more information.

Installation
------------

 - Put anthill.querytool in eggs= and zcml=
 - Make sure that AdvancedQuery is installed (works for Plone>=3.2)

 Example query
 -------------

 A query could look like that::

    And(
        Eq('SearchableText', '$text'),
        ~Generic('path', {'query':'Members', 'level':-1}),

        [[if($allowed_types)]]
            In('portal_types', $allowed_types),
        [[endif]]

        [[ifnot($allowed_types)]]
            In('portal_types', ['Folder', 'Document']),
        [[endif]]

        Ge('start_date', TODAY)
    )

Here you see that you can parametrize queries (using variable expansion using
$), you can use constants defined (only one currently active called TODAY
where TODAY=DateTime()) and you can put conditionals in your queries.
Conditionals are a powerful way to enable or disable certain parts of your
query. The ``if`` statement checks if a given parameter exists. You can also
replace ``if`` with ``ifnot``that only activates the given part if the
parameter is not set.

You can save this query and call it later on like that::

context.query_tool.executePredefinedQuery(
    'contentsearch', text='Test*', allowed_types=['Folder', ])

Screenshots:
------------

Submit query

.. image:: http://files.banality.de/public/anthill.querytool.submit.jpg

Predefined queries

.. image:: http://files.banality.de/public/anthill.querytool.predefined.jpg

