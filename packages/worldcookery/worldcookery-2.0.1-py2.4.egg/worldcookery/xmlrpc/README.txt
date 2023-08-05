=========================
XML-RPC views for recipes
=========================

This package contains XML-RPC views for recipes.  They allow client
applications to remotely query and possibly change the information
stored in recipe objects.

Consider the following demonstration.  First, we need a recipe object
to work with.  We simply simulate a recipe object being added through
a browser:

  >>> print http(r"""
  ... POST /@@contents.html HTTP/1.1
  ... Authorization: Basic mgr:mgrpw
  ... """, form={
  ...     'type_name': u'BrowserAdd__worldcookery.site.WorldCookerySite',
  ...     'new_value': u'wcsite'
  ... })
  HTTP/1.1 303 See Other
  ...

  >>> print http(r"""
  ... POST /wcsite/@@contents.html HTTP/1.1
  ... Authorization: Basic mgr:mgrpw
  ... """, form={
  ...     'type_name': u'BrowserAdd__worldcookery.folder.RecipeFolder',
  ...     'new_value': u'recipes'
  ... })
  HTTP/1.1 303 See Other
  ...

  >>> print http(r"""
  ... POST /wcsite/recipes/+/worldcookery.Recipe HTTP/1.1
  ... Authorization: Basic mgr:mgrpw
  ... """, form = {
  ...     'form.name': u'Miso soup',
  ...     'form.ingredients': [u'tofu', u'miso'],
  ...     'form.ingredients.marker': u'',
  ...     'form.tools-empty-marker': u'',
  ...     'form.time_to_cook': 20,
  ...     'form.description': u'Miso is a very popular Japanese soup.',
  ...     'form.actions.add': u'Add',
  ... })
  HTTP/1.1 303 See Other
  ...

Now we can query it using XML-RPC.  We call the ``info`` view with no
parameters and get back all of the information we put into the object
before, encoded in XML-RPC data.

  >>> print http(r"""
  ... POST /wcsite/recipes/Miso%20soup HTTP/1.0
  ... Authorization: Basic mgr:mgrpw
  ... Content-Length: 98
  ... Content-Type: text/xml
  ... 
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>info</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  Content-Length: 640
  Content-Type: text/xml;charset=utf-8
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><struct>
  <member>
  <name>time_to_cook</name>
  <value><int>20</int></value>
  </member>
  <member>
  <name>ingredients</name>
  <value><array><data>
  <value><string>tofu</string></value>
  <value><string>miso</string></value>
  </data></array></value>
  </member>
  <member>
  <name>tools</name>
  <value><array><data>
  </data></array></value>
  </member>
  <member>
  <name>description</name>
  <value><string>Miso is a very popular Japanese soup.</string></value>
  </member>
  <member>
  <name>name</name>
  <value><string>Miso soup</string></value>
  </member>
  </struct></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>

We can now even change the object's data through XML-RPC using the
`edit` view.  Note that we now need to identify ourselves using basic
HTTP authentication.

  >>> print http(r"""
  ... POST /wcsite/recipes/Miso%20soup HTTP/1.0
  ... Authorization: Basic mgr:mgrpw
  ... Content-Length: 748
  ... Content-Type: text/xml
  ... 
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>edit</methodName>
  ... <params>
  ... <param>
  ... <value><struct>
  ... <member>
  ... <name>time_to_cook</name>
  ... <value><int>25</int></value>
  ... </member>
  ... <member>
  ... <name>ingredients</name>
  ... <value><array><data>
  ... <value><string>tofu</string></value>
  ... <value><string>miso</string></value>
  ... <value><string>scallion</string></value>
  ... </data></array></value>
  ... </member>
  ... <member>
  ... <name>tools</name>
  ... <value><array><data>
  ... <value><string>big pot</string></value>
  ... </data></array></value>
  ... </member>
  ... <member>
  ... <name>description</name>
  ... <value><string>Miso soup is a very popular Japanese soup.</string></value>
  ... </member>
  ... <member>
  ... <name>name</name>
  ... <value><string>Miso soup</string></value>
  ... </member>
  ... </struct></value>
  ... </param>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  Content-Length: 153
  Content-Type: text/xml;charset=utf-8
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><string>Object updated successfully</string></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>

Finally, after having changed it, we can retrieve its data again just
to make sure everything is saved properly:

  >>> print http(r"""
  ... POST /wcsite/recipes/Miso%20soup HTTP/1.0
  ... Authorization: Basic mgr:mgrpw
  ... Content-Length: 98
  ... Content-Type: text/xml
  ... 
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>info</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  Content-Length: 726
  Content-Type: text/xml;charset=utf-8
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><struct>
  <member>
  <name>time_to_cook</name>
  <value><int>25</int></value>
  </member>
  <member>
  <name>ingredients</name>
  <value><array><data>
  <value><string>tofu</string></value>
  <value><string>miso</string></value>
  <value><string>scallion</string></value>
  </data></array></value>
  </member>
  <member>
  <name>tools</name>
  <value><array><data>
  <value><string>big pot</string></value>
  </data></array></value>
  </member>
  <member>
  <name>description</name>
  <value><string>Miso soup is a very popular Japanese soup.</string></value>
  </member>
  <member>
  <name>name</name>
  <value><string>Miso soup</string></value>
  </member>
  </struct></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>


Metadata
--------

Of course, we can also retrieve Dublin Core metadata through XML-RPC

  >>> print http(r"""
  ... POST /wcsite/recipes/Miso%20soup/@@EditMetaData.html HTTP/1.1
  ... Authorization: Basic mgr:mgrpw
  ... Content-Length: 84
  ... Content-Type: application/x-www-form-urlencoded
  ... """, form={
  ...     'dctitle': u'Miso soup',
  ...     'dcdescription': u'Miso soup is a very popular soup in Japan.',
  ...     'save': u'Save',
  ... })
  HTTP/1.1 200 Ok
  ...

Which we can easily query through XML-RPC using the ``dublincore_info``
method:

  >>> print http(r"""
  ... POST /wcsite/recipes/Miso%20soup HTTP/1.0
  ... Authorization: Basic mgr:mgrpw
  ... Content-Length: 109
  ... Content-Type: text/xml
  ... 
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>dublincore_info</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  Content-Length: 1073
  Content-Type: text/xml;charset=utf-8
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><struct>
  <member>
  <name>publisher</name>
  <value><string></string></value>
  </member>
  <member>
  <name>description</name>
  <value><string>Miso soup is a very popular soup in Japan.</string></value>
  </member>
  <member>
  <name>effective</name>
  <value><string></string></value>
  </member>
  <member>
  <name>title</name>
  <value><string>Miso soup</string></value>
  </member>
  <member>
  <name>expires</name>
  <value><string></string></value>
  </member>
  <member>
  <name>modified</name>
  <value><dateTime.iso8601>...</dateTime.iso8601></value>
  </member>
  <member>
  <name>created</name>
  <value><dateTime.iso8601>...</dateTime.iso8601></value>
  </member>
  <member>
  <name>subjects</name>
  <value><array><data>
  </data></array></value>
  </member>
  <member>
  <name>contributors</name>
  <value><array><data>
  </data></array></value>
  </member>
  <member>
  <name>creators</name>
  <value><array><data>
  <value><string>zope.mgr</string></value>
  </data></array></value>
  </member>
  </struct></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>
