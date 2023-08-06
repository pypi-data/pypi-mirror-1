How to use :mod:`pydataportability.xrd` in your project
=======================================================

Here is a quick example on how to use it for retrieving and parsing
and :term:`XRD` document:

.. code-block:: python

    from pydataportability.xrd.parser import parse_xrd

    fp = open('xrdfile.xrd','r')    
    resource = parse_xrd(fp)
    fp.close()
    
Of course you can also retrieve such a file via ``urlopen`` or similar 
methods. What you need is a file pointer though.

Now that it's parsed you can access the elements of the resource:

.. code-block:: python

    print resource.subject
    print resource.type
    print resource.expires # is a datetime object
    print resource.aliases # will return a list of URIs

You can also access the links pointing to other resources which are stored
in the ``links`` attribute. You can use the ``get_by_rel()`` in order to filter
for the relationship types you are interested in

.. code-block:: python

    rels = resources.links.get_by_rel("describedby")
    
Moreover you can use the ``filter()`` method if you want advanced filtering:

.. code-block:: python

    rels = resources.links.filter(rels=['describedby','webfinger'], 
                media_types=['application/xml+xrd'])
                
                
This example will filter out all relationships which do not have the
types ``describedby`` and ``webfinger`` together and additionally are of
the type ``application/xml+xrd``. So all these conditions are used as AND.

Now that you eventually have found some relationships you can access their
attributes:

.. code-block:: python
    
    print link.uris # a list of URI strings.
    print link.media_types # a list of media types for this relationship
    print link.subject # None or string
    print link.priority # integers
    print link.templates # this is a list if URI template objects
    



    
    



