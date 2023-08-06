commentator
===========

WSGI commenting middleware

To use
------

Make a factory wrapping your app in the commentator middleware.
Currently, commentator only pickles comments.  To the constructor of
Commentator, pass a database (the path to the pickle) and a pattern.
The pattern is in the form of

<URL pattern>#<xpath pattern> -> URL

The URL pattern is a 
`python regular expression <ttp://docs.python.org/library/re.html>`_
to match against the request's PATH_INFO.  

The xpath pattern is where you want to place the comments on the
page.  See http://www.w3schools.com/XPath/ for more about xpath
expressions.

The URL is a 
`python string template <http://docs.python.org/library/string.html>`_
that is substituted for groups in the URL regular expression and
element attributes in the found nodes.  The element attributes are
referenced by name (``${id}``, ``${class}``, etc) and the groups are
referenced by number (``${1}``, ...).


Example
-------

A reference implementation is illustrated in the commentator.ini
file.  This uses the pattern:

 ``commentator.pattern = (.*)#.//div[@id='comment_on_this'] -> ${1}``

What this pattern says is

 * comment on every PATH_INFO ``(.*)``
 * append the rendered content template to ``div[@id='comment_on_this']``
 * reference the PATH_INFO as the canonical URL ``${1}``

To comment on every HTML page at the end of the body, you would use

 ``commentator.pattern = (.*)#.//body -> ${1}``

A more complex example is in the ``.ini`` file, commented out, for use with
`bitsyblog <http://k0s.org/hg/bitsyblog>`_ :
 
  ``commentator.pattern = /blog/.*#.//div[@class='blog-entry'] -> /blog/${id}``

This pattern says:

 * comment on all paths under blog
 * put the comments at the end of each ``div[@class='blog-entry']``
 * get the URI from the ``div``'s id, not from the ``PATH_INFO``


TODO
----

This is very alpha.  I'd be happy to work more on this if anyone wants
it.  A few outstanding issues:

 * fix weird lxml issue where you have to put .// for elements
 * allow commenting on multiple resources (multiple patterns per instance)
 * locking pickle files
 * fix couch....not sure what's wrong
 * allow use of CSS classes, not just xpath

--

http://k0s.org
