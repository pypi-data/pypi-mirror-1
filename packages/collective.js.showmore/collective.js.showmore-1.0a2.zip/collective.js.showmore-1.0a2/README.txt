collective.js.showmore
======================

Introduction
------------

`collective.js.showmore` provides a JQuery plugin.

The plugin hides a set of nodes and replaces them with a "Show more..." link.
When the link is clicked, the hidden nodes are made visible again.


API
---

The plugin defines a new `showMore` function.
It requires a dictionary as parameter.

The dictionary parameter has one required value:

`expression`
    The expression is a JQuery selector used to select which children nodes
    will be hidden.  In case no nodes are hidden, the link is not created.

The dictionary parameter can optionally define four other values:

`link_text`
    Defines the text of the link; default value is "Show more...".

`link_class`
    Defines the class added on the link; default value is `showMoreLink`.

`hidden_class`
    Defines the class set on the hidden nodes; default value is
    `showMoreHidden`.

`grace_count`
    Defines how many items should not be hidden; default value is 1.
    In the default case, if there is only one item that would be hidden, do
    not hide and replace it with the link.


Example
-------

The function can be called like the following::

    jq(function() {
        jq('ul').showMore({expression:'li:gt(1)'});
    });

`li` children nodes of all `ul`'s of the document will be hidden (except the
two first `li`s of each `ul`). A "Show more..." link will be added at the end
of each `ul`. `ul`'s with two or less `li`'s will remain untouched.


Miscellaneous
-------------

The Javacript code is registered as a Z3 resource::

    ++resource++collective.showmore.js
