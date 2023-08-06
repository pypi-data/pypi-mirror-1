Dreamweaver Support
+++++++++++++++++++

The :mod:`dreamweavertemplate` module provides support for working
with templates and library items in Dreamweaver format.

.. caution ::

   Since I don't actually have a copy of Dreamweaver I haven't been able to test
   that what I've implemented here is actually compatible with Dreamweaver. That
   actually doesn't matter to me too much because its the functionality I'm 
   after, not the compatibility. That said, I would like to know if it is 
   compatible and would be happy to accept patches with tests.

.. caution ::

   The software relies on the ``posixpath`` module which isn't available for 
   Windows.

Introduction
=============

Simple Example
---------------

As an example consider this template (based on a real example used to generate
the pythonweb.org website back in 2002):

::

    >>> main_template = """\
    ... <?xml version="1.0" encoding="iso-8859-1"?>
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
    ...   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html xmlns="http://www.w3.org/1999/xhtml">
    ... <head>
    ... <!-- TemplateBeginEditable name="doctitle" -->
    ... <title>Python Web Project</title>
    ... <!-- TemplateEndEditable --> 
    ... <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    ... <link href="../css/style.css" rel="stylesheet" type="text/css" />
    ... <!--     TemplateBeginEditable name="head" --><!--  TemplateEndEditable -->
    ... </head>
    ... <body>
    ... <!--
    ... Copyright 2002-2004 James Gardner All Rights Reserved.
    ... -->
    ... <div id="body1"> 
    ...      <div id="nav1"> 
    ... <!-- #BeginLibraryItem  "../Library/main_links.lbi" -->
    ... <ul>
    ...     <li id="active"><a href="../index.html" id="current">Home</a></li>
    ...     <li><a href="../projects/index.html">Projects</a></li>
    ...     <li><a href="../contribute/index.html">Contribute</a></li>
    ...     <li><a href="../technology/index.html">Technology</a></li>
    ...     <li><a href="../about/index.html">About</a></li>
    ...     <li><a href="../contact/index.html">Contact </a></li>
    ... </ul>
    ... <!--  #EndLibraryItem   -->
    ...     </div>
    ...     <div id="content1"> 
    ...         <!-- Begin Content -->
    ...         <h2 class="heading">
    ...             <!-- TemplateBeginEditable name="tagLine" -->PythonWeb<!-- 
    ...             TemplateEndEditable -->
    ...         </h2>
    ...         <p class="indent1">
    ...             <!-- TemplateBeginEditable name="subParagraph" -->
    ...                 <span class="small">This involves desinging and
    ...                     writing the necessary modules, packaging 
    ...                     distributions and documenting the modules with 
    ...                     examples and tutorials as well as spreading the
    ...                     word about Python. 
    ...                     <a href="./">Read more &raquo;</a>
    ...                 </span>
    ...             <!-- TemplateEndEditable -->
    ...         </p>
    ...         <!-- End Content -->
    ...     </div>
    ...     <div id="footer">
    ...         <!-- TemplateBeginEditable name="Footer" -->
    ...         <!-- #BeginLibraryItem "../Library/footer.lbi" -->
    ...         <p class="footer">Copyright &copy; 2002-2005 James Gardner All
    ...         Rights Reserved.<br />
    ...         <i>62,561 page views since launch on 04th October 2004 until 
    ...         the end of 2004</i></p>
    ...         <!-- #EndLibraryItem -->
    ...         <!-- TemplateEndEditable -->
    ...     </div>
    ... </div>
    ... </body>
    ... </html>"""
    >>>

Notice that there is extra whitespace in some of the comments. This module can
deal with extra whitespace.

Let's look at the other components of this template:

::

    >>> main_links_library_item = """\
    ... <ul>
    ...     <li id="active"><a href="../index.html" id="current">Home</a></li>
    ...     <li><a href="../projects/index.html">Projects</a></li>
    ...     <li><a href="../contribute/index.html">Contribute</a></li>
    ...     <li><a href="../technology/index.html">Technology</a></li>
    ...     <li><a href="../about/index.html">About</a></li>
    ...     <li><a href="../contact/index.html">Contact </a></li>
    ... </ul>"""
    >>>
    >>> footer_library_item = """\
    ...         <p class="footer">Copyright &copy; 2002-2005 James Gardner All
    ...         Rights Reserved.<br />
    ...         <i>62,561 page views since launch on 04th October 2004 until 
    ...         the end of 2004</i></p>"""
    >>> 

Let's create a directory structure containing these templates and library
items:

::

    >>> import os
    >>> test_dir = 'example_dir'
    >>> if os.path.exists(test_dir):
    ...     raise Exception("The %s directory already exists"%test_dir)
    ... else:
    ...     os.mkdir(test_dir)
    ...     os.mkdir(os.path.join(test_dir, 'downloads'))
    ...     os.mkdir(os.path.join(test_dir, 'Templates'))
    ...     fp = open(os.path.join(test_dir, 'Templates', 'main.dwt'), 'w')
    ...     fp.write(main_template)
    ...     fp.close()
    ...     os.mkdir(os.path.join(test_dir, 'Library'))
    ...     fp = open(os.path.join(test_dir, 'Library', 'main_links.lbi'), 'w')
    ...     fp.write(main_links_library_item)
    ...     fp.close()
    ...     fp = open(os.path.join(test_dir, 'Library', 'footer.lbi'), 'w')
    ...     fp.write(footer_library_item)
    ...     fp.close()
    >>>
    
Working with Regions
--------------------

Now let's create a new file from the ``main.dwt`` template:

::

    >>> from dreamweavertemplate import DreamweaverTemplateInstance
    >>> new_page = DreamweaverTemplateInstance(
    ...     filename=os.path.join(test_dir, 'Templates', 'main.dwt')
    ... )
    
The ``new_page`` instance behaves a bit like a dictionary. You can access its
regions like this (ignoring blank lines):

::

    >>> print new_page['doctitle'].strip('\n')
    <title>Python Web Project</title>
   
and set new content for a region like this:

::

    >>> new_page['Footer'] = 'This is the new footer'
    >>> print new_page['Footer']
    This is the new footer

You can append content to the end of a region using the ``+=`` operator:

::

    >>> new_page['Footer'] += ' with more content'
    >>> print new_page['Footer']
    This is the new footer with more content

You can't create new regions:

::

    >>> new_page['new_region'] = 'This is a new region'
    Traceback (most recent call last):
      File ...
    TemplateError: Error, 'new_region' is not an editable region of the template.

Saving Templates
----------------

Finally print the whole document complete with the altered editable regions.
I've missed out most of the content and just shown the footer so you can see
that it has changed:

::

    >>> print new_page.save_as_template()
    <?xml version="1.0" encoding="iso-8859-1"?>
    ...
        <div id="footer">
            <!-- TemplateBeginEditable name="Footer" -->This is the new footer with more content<!-- TemplateEndEditable -->
        </div>
    ...
    </html>

If you don't give a name the current template filename is used.  If you want to
save the template to disk as another template you only need to specify the
path. You should only save files in the ``Templates`` directory:

    >>> new_page.save_as_template(os.path.join(test_dir, 'new.dwt'))

Pages relying on the template are not updated automatically when you save a
template, you need to perform updates manually. See later.

Tidying Source Code
-------------------

The ``save_as_template()`` method can use uTidyLib to tidy up your HTML. The
library can be installed like this:

::

    $ easy_install http://download.berlios.de/utidylib/uTidylib-0.2.zip

It can be used standalone like this:

    >>> import tidy
    >>> options = dict(output_xhtml=1, 
    ...                add_xml_decl=1, 
    ...                indent=1, 
    ...                tidy_mark=0)
    >>> print tidy.parseString('<Html>Hello Tidy!', **options)
    <?xml version="1.0" encoding="us-ascii"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title></title>
      </head>
      <body>
        Hello Tidy!
      </body>
    </html>
    <BLANKLINE>

It is used with ``save_as_template()`` like this:

::

    >>> print new_page.save_as_template(tidy=True)
    <?xml version="1.0" encoding="iso-8859-1"?>
    ...
          <div id="footer">
            <!-- TemplateBeginEditable name="Footer" -->This is the new footer
            with more content<!-- TemplateEndEditable -->
          </div>
    ...
    </html>
    <BLANKLINE>

Notice that the template has been tidied up and formatted to a 78 character
line width.

.. warning ::

    Tidying up HTML might sound like a good idea but it has two problems:

    * It may make the file size larger due to extra indentation
    * If you aren't used to writing very good quality HTML and CSS then 
      re-formatting your HTML might affect the way it behaves
    * If you have written invalid HTML, tidying it up might result in 
      extra tags being added which again could change the way you indended
      it to appear.

    On the other hand, if you tidy up your HMTL and it still renderd correctly
    you can be fairly confident it is robust HTML.

Saving Pages
------------

The same template instance can also be saved as a page with the
``save_as_page()`` method. This takes a number of options:

``filename``
    An optional filename to save the page to. If not specified, the page is 
    just returned as a string.

``old_path``

``new_path``
    If the filename is not specified, the path to assume the file would be
    saved needs to be specified so that links in the template or library items
    can be correctly updated.

``tidy``
    Specifies whether the *regions* should be tidied up

    .. warning ::
       
       This tidies up the **entire page** not just the regions so could result
       in a page which is no longer exactly the same as the template on which
       it is based.

``update_library_items``
    Defaults to ``True`` causing any library items contained within the 
    regions to be updated.

XXX Should the regions be updated or not, at the moment they are.

When the page is saved, all the library items in the regions are updated. It is
assumed any library items in the template are already up to date. It is also
assumed the content you are adding to the page will need no adjustment but if
it does, you can use the ``update_links()`` function which looks like this:

::

    >>> from dreamweavertemplate import update_links
    >>> content = """\
    ...     <p><a href="../files/file1.zip">Download file 1</a><p>
    ...     <p><a href="../files/">Files</a><p>
    ...     <p><a href=".">Download List</a><p>"""
    >>> print update_links(
    ...     site_root = test_dir, 
    ...     old_path = os.path.join(test_dir, 'download', 'files.html'),
    ...     new_path = os.path.join(test_dir, 'files', 'index.html'), 
    ...     content = content,
    ... )
        <p><a href="file1.zip">Download file 1</a><p>
        <p><a href="./">Files</a><p>
        <p><a href="../download/">Download List</a><p>

Here ``site_root`` is the full path to the directory which the ``Templates``
and ``Library`` folders are contained in, the ``old_path`` is the full
path to where the page containing the links used to be and ``new_path`` is
the full path to where the page will be after the move.

Notice that all the links have been updated and directory names still correctly
end with a ``/`` character.

::

    >>> print new_page.save_as_page(new_path=os.path.join(test_dir, 'page.html'))
    <?xml version="1.0" encoding="iso-8859-1"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"><!-- InstanceBegin template="Templates/main.dwt" codeOutsideHTMLIsLocked="false" -->
    <head>
    <!-- InstanceBeginEditable name="doctitle" -->
    <title>Python Web Project</title>
    <!-- InstanceEndEditable --> 
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <link href="css/style.css" rel="stylesheet" type="text/css" />
    <!--     InstanceBeginEditable name="head" --><!--  InstanceEndEditable -->
    </head>
    <body>
    <!--
    Copyright 2002-2004 James Gardner All Rights Reserved.
    -->
    <div id="body1"> 
         <div id="nav1"> 
    <!-- #BeginLibraryItem  "Library/main_links.lbi" -->
    <ul>
        <li id="active"><a href="index.html" id="current">Home</a></li>
        <li><a href="projects/index.html">Projects</a></li>
        <li><a href="contribute/index.html">Contribute</a></li>
        <li><a href="technology/index.html">Technology</a></li>
        <li><a href="about/index.html">About</a></li>
        <li><a href="contact/index.html">Contact </a></li>
    </ul>
    <!--  #EndLibraryItem   -->
        </div>
        <div id="content1"> 
            <!-- Begin Content -->
            <h2 class="heading">
                <!-- InstanceBeginEditable name="tagLine" -->PythonWeb<!-- 
                InstanceEndEditable -->
            </h2>
            <p class="indent1">
                <!-- InstanceBeginEditable name="subParagraph" -->
                    <span class="small">This involves desinging and
                        writing the necessary modules, packaging 
                        distributions and documenting the modules with 
                        examples and tutorials as well as spreading the
                        word about Python. 
                        <a href="Templates/">Read more &raquo;</a>
                    </span>
                <!-- InstanceEndEditable -->
            </p>
            <!-- End Content -->
        </div>
        <div id="footer">
            <!-- InstanceBeginEditable name="Footer" -->This is the new footer with more content<!-- InstanceEndEditable -->
        </div>
    </div>
    </body>
    <!-- InstanceEnd --></html>

We have to specify the ``new_path`` argument so that the ``save_as_page()``
method can re-calculate links, even if you aren't specifying a filename to save
to.

::

    >>> new_page.save_as_page(filename=os.path.join(test_dir, 'page.html'))

Notice how all the links in the both the page template and the library items
have been corrected so that they work using relative paths at the new location.

Extra ``DreamweaverTemplateInstance`` Functionality
---------------------------------------------------

Here's a simpler example with some other useful methods:

::

    >>> simple_template = """\
    ... <?xml version="1.0" encoding="iso-8859-1"?>
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
    ...   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html xmlns="http://www.w3.org/1999/xhtml">
    ... <head>
    ... <title>Simple Page</title>
    ... </head>
    ... <body>
    ... <!-- TemplateBeginEditable name="a" -->A<!-- TemplateEndEditable -->
    ... <!-- TemplateBeginEditable name="b" -->B<!-- TemplateEndEditable -->
    ... <!-- TemplateBeginEditable name="c" -->C<!-- TemplateEndEditable -->
    ... </body>
    ... </html>
    ... """
    >>>
    >>> from dreamweavertemplate import DreamweaverTemplateInstance
    >>> simple_page = DreamweaverTemplateInstance(template=simple_template)
    >>> print simple_page.keys()
    ['a', 'c', 'b']
    >>> print simple_page.has_key('Content')
    False
    >>> print simple_page.items()
    [('a', 'A'), ('c', 'C'), ('b', 'B')]

Dealing with Pages
==================

Now you know how to work with tempates and how to create pages from them, let's
look at working with pages.

::

    >>> page = DreamweaverTemplateInstance(filename=os.path.join(test_dir, 'page.html'))
    >>> print page
    <DreamweaverTemplateInstance (instance), example_dir/page.html>
    >>> page.page_regions.keys()
    [u'doctitle', u'tagLine', u'head', u'subParagraph', u'Footer']

You can also see which template it uses:

::

    >>> page.template_path == os.path.join(os.getcwd(), test_dir, 'Templates', 'main.dwt')
    True


