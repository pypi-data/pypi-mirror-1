This middleware is looks for a `_filter` query string in a request. If it is
present and the response has a content-type of `text/html` only the element
with the given id will be returned. If the id is not found in the response
an empty `div` element will be returned.

To illustrate this behaviour lets assume that a backend server generates this
response:

.. code-block:: html

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Test document</title>
      </head>
      <body>
        <h1 id="header">Test document</h1>
        <div id="body">
          <p>Welcome to our little test</p>
        </div>
      </body>
    </html>

If a browsers requests this document using a request for
`http://www.example.com/` the document will be returned untouched.

Lets suppose that AJAX capability is being added to your site and you
need to inject theheadertitle from this document. Instead of requesting the
full document and extracting the element with the `header` id you can
ask `repoze.slicer` to do the filtering by making a request for
`http://www.example.com/?_filter=header`. The returned data will then look
like this:

.. code-block:: html

    <h1 id="header">Test document</h1>


Caveats
-------

* Only responses with a status code of 200 are filtered.

* Only valid XML documents can be processed. Responses which can not
  be parsed using the `lxml` XML parser will be returned unmodified.


Adding :mod:`repoze.slicer` To Your WSGI Pipeline
-------------------------------------------------

Via ``PasteDeploy`` .INI configuration::

  [pipeline:main]
   pipeline =
           egg:repoze.slicer
           myapp

Via Python:

.. code-block:: python

  from otherplace import mywsgiapp

  from repoze.slicer import SlicerApp
  new_wsgiapp = SlicerApp(mywsgiapp)



