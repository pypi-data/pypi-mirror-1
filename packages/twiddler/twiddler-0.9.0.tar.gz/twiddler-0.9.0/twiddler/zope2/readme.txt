Twiddler for Zope 2

  Installation

    Twiddler is a python package and, as such, is installed by placing
    the 'twiddler' folder somewhere on your PYTHONPATH.

    For Zope 2, this will likely mean the the lib/python directory of
    either your instance home or software home.

    For Twiddler to work, the following python packages need to be
    available on your PYTHONPATH:

    - elementtree
   
      Even though this comes as standard in Python 2.5 or above,
      Twiddler has not yet been made compatible with the version that
      ships with Python 2.5. ElementTree must be seperately installed
      no matter what version of Python you are using and it can be
      downloaded from:

      http://effbot.org/zone/element-index.htm

    In addition, to use Twiddler with Zope 2, you need to be using
    Zope 2.10.0 or above.

    Once the python packages are installed on the PYTHONPATH, Twiddler
    can be enabled by including the following zcml snippet in an
    appropriate location such as etc/site.zcml in your Zope instance:

    <include package="twiddler.zope2" />

    The above must be included before the following bits which are
    usually also found in site.zcml:

    <five:loadProducts />
    <five:loadProductsOverrides />

  Usage

    Twiddlers in Zope 2 can be instantiated either through the ZMI or
    programatically. Throughout these examples, we will use
    programatic examples while explaining the ZMI equivalents.

    To instantiate a Twiddler, we use a normal Zope 2 factory:

    >>> folder.manage_addProduct['twiddler.zope2'].addTwiddler('test')
    >>> t = folder.test
    
    Our new Twiddler can already be rendered:

    >>> print t()
    <node id="test" />

    The form for editing the source of the Twiddler can be found by
    clicking on the newly created Twiddler in the ZMI. We simulate
    this here by rendering the form, we store the output rather than
    displaying it to save space.

    >>> print len(t.sourceForm())
    2533

    You can now enter the necessary source and then hit the save
    button and see the resulting message indicating that your changes
    have been saved:

    >>> print len(t.setSource('''<html>
    ... <body>
    ... <p id="content">my content!</p>
    ... </body>
    ... </html>''',request))
    2688

    You can load Twiddlers via WebDAV:

    >>> print t.manage_DAVget()
    <html>
    <body>
    <p id="content">my content!</p>
    </body>
    </html>

    You can also save Twiddlers via WebDAV:

    >>> request.set('BODY','''<parent id="parent">
    ... <child id="child"/>
    ... </parent>''')
    >>> t.PUT(request,request.RESPONSE)
    HTTPResponse('')
 
    We can see that the response status has been set to 204 indicating
    our changes have been successfully saved:

    >>> print request.RESPONSE.getStatus()
    204

    We can also see our changes by rendering the Twiddler:

    >>> print t.render()
    <parent id="parent">
    <child id="child" />
    </parent>

    At this point, it's important to explain how Twiddler works with
    Zope 2's security model. Manipulating a Twiddler as we have done
    above requires the user to have the 'Manage Twiddler' permission,
    since the manipulations will actually alter the persistent
    Twiddler instance stored in the ZODB.

    As a result, you may be wondering how a normal user without the
    'Manage Twiddler' permission can render a Twiddler. The answer is
    that Twiddler's 'clone' method returns a different type of object
    when used in a Zope 2 context. The returned object can be
    manipulated and rendered by anyone with the 'View' permission.

    We'll show this by logging in as an anonymous user:

    >>> from AccessControl.SecurityManagement import noSecurityManager
    >>> noSecurityManager()

    We now use a python script to manipulate and render a
    Twiddler. Python scripts operate in a resricted environment, so
    this shows how an anonymous user can perform actions on a clone of
    a Twiddler, even though they cannot modify the source Twiddler:

    >>> t.setSource('''<html>
    ... <body>
    ... <ul id="nested"><li id="child" /></ul>
    ... <p id="sequence">my content 1</p>
    ... </body>
    ... </html>''')
    >>> addPythonScript(folder,'script','''
    ... t = container.test.clone()
    ... n = t['nested'].clone()
    ... t['child'].replace(n,id=False)
    ... r = t['sequence'].repeater()
    ... for i in range(3):
    ...   r.repeat(
    ...   'my content '+str(1),
    ...   id='s'+str(i)
    ...   )
    ... return t.render()
    ... ''')
    >>> print folder.script()
    <html>
    <body>
    <ul id="nested"><ul><li id="child" /></ul>
    </ul>
    <p id="s0">my content 1</p>
    <p id="s1">my content 1</p>
    <p id="s2">my content 1</p>
    </body>
    </html>

    Some Twiddler components can be configured through Zope's
    management interface using the Configure tab:

    >>> print len(t.configureForm())
    3383

    We can select another input parser. In the example below, we
    select the plain text input parser:

    >>> print len(t.setComponent('input','Plain Text',request))
    3453

    For this to work, we need to change the source:

    >>> t.setSource('<block>Item $item_no</block>\n')

    We can now make changes and render the Twiddler as normal:

    >>> c = t.clone()
    >>> r = c['block'].repeater()
    >>> for i in range(1,4):
    ...   e = r.repeat()
    ...   e['item_no'].replace(i)
    >>> print c.render().strip()
    Item 1
    Item 2
    Item 3

    By default, Zope 2 Twiddlers have no executor. We can supply one
    in a way similar to changing the input parser above. In the
    example below, we introduce a Traversal executor:

    >>> t.setComponent('executor','Traverse')

    This executor traverses to a path in the Zope object database and
    uses the object found to manipulate the Twidder.

    To demonstrate this, we will use the following python script as
    our executor:

    >>> addPythonScript(folder,'executor_script','''
    ... ##parameters=t
    ... c = t.clone()
    ... r = c['block'].repeater()
    ... for i in range(1,4):
    ...   e = r.repeat()
    ...   e['item_no'].replace(i)
    ... return c
    ... ''')
    
    Now, we configure our traversal executor to use this python
    script:
  
    >>> request.form['path']='/folder/executor_script'
    >>> print len(t.configureComponent('executor',request))
    3802

    Finally, we can render our executor:

    >>> print t.render().strip()
    Item 1
    Item 2
    Item 3
