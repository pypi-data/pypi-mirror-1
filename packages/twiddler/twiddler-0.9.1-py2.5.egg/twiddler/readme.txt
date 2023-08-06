Twiddler seeks to provide a way to render textual content from
template sources. It has two main aims:

- be able to work with source material provided by designers and
  leaving them absolutely unchanged or work absolutely seamlessly
  with visual editors if there is any markup that needs to be
  added.

- be absolutely as simple as possible while still being able to
  handle all that needs to be done. This, in particular, means no
  new languages should need to be known to be use Twiddler!

Before You Start
================

You will need to know the syntax of the content you wish to
generate, be that XML, HTML or plain text.

You will need to know some Python. You'll need to know very little
to get going, but if you want to do more advanced manipulation,
you'll need to know more.

Installation
============

The easyiest way to install Twiddler is:

  easy_install twiddler

Or, if you're using zc.buildout, just specify 'twiddler' as 
a required egg.

However, you can also install by unpacking the source
distribution and placing the 'twiddler' folder somewhere on your 
PYTHONPATH.

If you do not install using easy_install or zc.buildout, you will 
also need to make sure the following python packages are available 
on your PYTHONPATH:

- **elementtree**
   
  Even though this comes as standard in Python 2.5 or above,
  Twiddler has not yet been made compatible with the version that
  ships with Python 2.5. ElementTree must be seperately installed
  no matter what version of Python you are using and it can be
  downloaded from:

  http://effbot.org/zone/element-index.htm
    
- **zope.interface**

  This comes as standard in Zope 2.9.0 and above, but if you're
  not using Zope, you'll need to download it from:

  http://download.zope.org/distribution/

  You'll need a knowledge of python eggs although the INSTALL.TXT
  in the .tar.gz file gives instructions.

- **zope.testing**

  This is only needed if you want to run the included unit and doc
  tests. It comes as standard in Zope 2.9.0 and above, but if
  you're not using Zope and want to run the tests, it can be
  seperately downloaded from:

  http://download.zope.org/distribution/

  You'll need a knowledge of python eggs although the INSTALL.TXT
  in the .tar.gz file gives instructions.

  For instructions on installation with the various python web
  frameworks, please see the "Further Information" section below.

Usage
=====

To explain how Twiddlers work, we're going to use the plain python
version of Twiddler and do everything from scratch. Once you've
installed Twiddler for plain python, the following examples will
all work just fine.

So, to start off with, you create a Twiddler from some source
string:
 
  >>> from twiddler import Twiddler
  >>> t = Twiddler('''<html>
  ...   <body>
  ...   <div id="greeting">Hello world!</div>
  ...   <div name="stuff">I'm in <i>Italic</i>!</div>
  ...   <form><input name="test" value="value"/></form>
  ...   </body>
  ... </html>''')

From then on, you make the content dynamic by finding an element
and then either replacing parts of it, removing it or repeating
it. This can be done as often as you like. At any point, you can
call the Twiddler's render method to get a string that you can
return to the browser.

Here's a couple of simple examples of replacement:

  >>> t['greeting'].replace('Hello user!',style='color: red;')
  >>> t['test'].replace(value='my value')

We can see the results by rendering the Twiddler:

  >>> print t.render()
  <html>
    <body>
    <div id="greeting" style="color: red;">Hello user!</div>
    <div name="stuff">I'm in <i>Italic</i>!</div>
    <form><input name="test" value="my value" /></form>
    </body>
  </html>

Here's a simple example of removal:

  >>> t['stuff'].remove()
  >>> print t.render()
  <html>
    <body>
    <div id="greeting" style="color: red;">Hello user!</div>
    <form><input name="test" value="my value" /></form>
    </body>
  </html>

Here's a simple example of repeating:
    
  >>> e = t['greeting'].repeater()
  >>> for i in range(3):
  ...   e.repeat('Hello user %i!'%i,id='greeting'+str(i))    
  <twiddler.TwiddlerElement instance at ...>
  <twiddler.TwiddlerElement instance at ...>
  <twiddler.TwiddlerElement instance at ...>

  >>> print t.render()
  <html>
    <body>
    <div id="greeting0" style="color: red;">Hello user 0!</div>
    <div id="greeting1" style="color: red;">Hello user 1!</div>
    <div id="greeting2" style="color: red;">Hello user 2!</div>
    <form><input name="test" value="my value" /></form>
    </body>
  </html>

You may be wondering where the <twiddler.twiddler...> lines in the
output above are coming from. Well, they're an artifact of how the
python shell behaves, but one caused by another feature.

The repeat method returns the element that has just been
inserted. This is useful if you want to repeat more complex
structures:

  >>> t = Twiddler('''<html>
  ...   <body>
  ...   <div name="row">This is row <i name="number">1</i></div>
  ...   </body>
  ... </html>''')
  >>> e = t['row'].repeater()
  >>> for i in range(3):
  ...    c = e.repeat()
  ...    c['number'].replace(str(i),name=False)
  >>> print t.render()
  <html>
    <body>
    <div name="row">This is row <i>0</i></div>
    <div name="row">This is row <i>1</i></div>
    <div name="row">This is row <i>2</i></div>
    </body>
  </html>
    
Now, you may have noticed that, so far, we've done all
manipulation of the elements from code outside of the source
code. Some people find the duality of source and code that
manipulates the source, particularly when they're likely to be in
different files on disk, unpleasant. To make life happier for
these people, Twiddler supports the inclusion of a code block in
the source itself as follows:

  >>> from twiddler.input.default import DefaultWithCodeBlock
  >>> t = Twiddler('''<html>
  ... <!--twiddler 
  ... def myfunc(t):
  ...   e = t['row'].repeater()
  ...   for i in range(3):
  ...     c = e.repeat()
  ...     c['number'].replace(str(i),name=False)
  ... -->
  ...   <body>
  ...   <div name="row">This is row <i name="number">1</i></div>
  ...   </body>
  ... </html>''',input=DefaultWithCodeBlock)

This code is executed when the render method is called:

  >>> print t.render()
  <html>
    <body>
    <div name="row">This is row <i>0</i></div>
    <div name="row">This is row <i>1</i></div>
    <div name="row">This is row <i>2</i></div>
    </body>
  </html>

You'll notice that to get this to work, a different input parser
has to be specified. This is because code block execution can pose
a significant security problem when the source of the Twiddler
comes from user input and so the default parser that
Twiddler uses will not look for code to execute.

Now, when generating HTML, you often want to have a common style
across many pages. Twiddler lets you do this by allowing you to
insert parts of one Twiddler into another. 

So, for example, here's our site template:

  >>> template = Twiddler('''<html>
  ...   <body>
  ...   <h1>The Site Header</h1>
  ...   <div id="content">Content goes here</div>
  ...   </body>
  ... </html>''')
    
And here's a specific page:

  >>> page = Twiddler('''
  ... <html>
  ...   <body>
  ...   <div id="content">This is our page content!</div>
  ...   </body>
  ... </html>
  ... ''')
    
Now, to put them together we do the following:

  >>> t = template.clone()
  >>> t['content'].replace(page['content'])
  >>> print t.render()
  <html>
    <body>
    <h1>The Site Header</h1>
    <div id="content">This is our page content!</div>
    </body>
  </html>

Finally, at any point, Twiddler's can be pickled:

  >>> from cPickle import dumps,loads
  >>> s = dumps(t)

This allows them to be saved to disk in a partially rendered
state. This should provide some great opportunities for speeding
up page rendering by only having to render the changes you need to
make, when you need to make them.

For example, the Twiddler we have just pickled could be reloaded,
and just the content replaced, without having to be-build the page
from the seperate page and template components:

  >>> from_cache = loads(s)
  >>> from_cache['content'].replace('Our new content!')
  >>> print from_cache.render()
  <html>
    <body>
    <h1>The Site Header</h1>
    <div id="content">Our new content!</div>
    </body>
  </html>

Further Information
===================

More detailed information on each of Twiddler's aspects can be
found in the 'docs' directory of the distribution:

*replace.txt*
  covers all possible uses of the replace method

*repeat.txt*
  covers all possible uses of the repeat method

*search.txt*
  covers all the ways you can search for elements

*filters.txt*
  covers the use of filters for specific calls to replace and
  repeat along with setting up default filters such as html quoting
  and internationalisation. 

*inandout.txt*
  covers the usage of Twiddler with different input parsers
  and output renderers. This also covers the default parse and render
  objects in more detail. 

*execution.txt*
  covers all the ways that code can be executed as
  a result of calling either the render of execute
  methods. 

*templating.txt*
  covers the render, execute and clone methods as
  used to build complete output from multiple
  Twiddlers.

In addition, the interfaces implemented by the various components
that make up Twiddler are described in interfaces.py in the
'twiddler' package.

Instructions and examples for using Twiddler with various python
web frameworks can also be found in the following files, contained
within their sub-packages:

*zope2/readme.txt*
  covers usage of Twiddler in plain Zope 2.

Licensing
=========

Copyright (c) 2006-2008 Simplistix Ltd

This Software is released under the MIT License:
http://www.opensource.org/licenses/mit-license.html
See license.txt for more details.

Credits
=======

**Chris Withers**
  Idea and development

**Fredrik Lundh**
  The excellent ElementTree library

**The Django Guys**
  For the idea of filters

**Guido van Rossum**
  For being stubborn enough about XML that I thought more
  deeply about parsing and rendering ;-)

Changes
=======

0.9.1
-----

- change readme.txt to reStructuredText

- fix syntax errors in prototype benchmark files.

0.9.0
-----

- changes to work with distutils, setuptools and zc.buildout

0.8.0 
-----

- Initial Release

To-Do
=====

0.10.0
------

- Tests and docs for new interfaces (particular attributes and setSource)
  (frameworks.txt?)

- check that if input returns no executor, don't overwrite any
  existing executor

- setSource replaces executor if supplied

- render.py example

- ability to remove specified attributes in the default renderer

- attribute and value introspection
  (what to do about nested values? what output to use? default?)

- to go back into filters.txt:

    You may be wondering how to translate text in "non-dynamic" parts of
    a Twiddler, such as the "hello" attribute and value in the following
    example: 

    >> t = Twiddler('<tag attr="hello">hello</tag>',indexes=('attr',))

    Well, the answer is relatively simple:
 
    >> t['hello'].replace(True,attr=True,filters=(translate,))
    >> print t.render()

    One final note; any filters passed either during twiddler
    instantiation or to the setFilters method must be pickleable.

1.0 
---

- Zope 3 support

- performance metrics
  Zope 3 ZPT

- performance metrics
  Zope 2 ZPT

Non-Version Specific
--------------------

- i18n

- xpath searching?
>>>>>>> .merge-right.r3425
