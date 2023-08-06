====================
SweetPotatoPy README
====================

This file contains all of the documentation included inline in SweetPotatoPy.


Main Module Docs
================
This is a page publication system designed to demonstrate the PyTin CGI
framework. This file will function as a CGI script, but for extra security you
can use PyTin's Prebake functions (type ``python -m pytin`` at the shell prompt)
to generate a prebake script you can use instead.

The home directory is a directory you create that will hold all your content and
support files. For more info on how to lay it out, see the docs for the function
``open_home``.

Note that one important setting needs to be changed to get SweetPotatoPy to
work. All configuration EXCEPT one item is stored in the home directory, but
SPP needs to know where the directory is - which is the one item. If you're
using this file as a CGI script, near the top change the SPP_HOME_DIRECTORY
variable (it's on line 47). If you're using it as a prebake, change this line ::
    
    bake(spp.run)

to ::
    
    bake(spp.run, home="/your/spp/home/directory/here/without/trailing/slash")


Directory Structure
===================
Your directory structure should look something like:

``spp.ini``
    This is your main config file. You can generate a sample by running the
    function ``example_config_file()``.
    
``navbar.ini``
    This is your navbar config file. Read the help for ``gen_navbar`` for info
    on structuring said file.

``templates/``
    This should have folders. Inside said folders, there should be Jinja
    templates. Read the docs for ``do_template`` for more info. You'll need to
    have one folder set in the config file's ``templates/default_folder``, and
    a filename under ``main_template`` that exists in that folder.

``pages/``
    Pages should go here, with the extension ``.spp``. The pages can be grouped
    into subfolders, and the subfolders can be accessed. This should be secure,
    so long as you **DO NOT PUT SYMBOLIC LINKS IN THIS FOLDER**.

``blocks/``
    Blocks go here, in reStructuredText format. Blocks must be defined in your
    config file under the ``blocks`` heading, with the key referring to a block
    name and the value being a file within this directory.


Example Config File
===================
::
 
 [siteinfo]
 name=Test Site
 descr=A test site for SweetPotatoPy.
 maintainer=Steve Person
 contactmail=steveperson@sppiscool.example
 
 [navigation]
 homepage=welcome
 
 [templates]
 defaultdir=basic
 maintemplate=index.html
 
 [blocks]
 footer=footer.spp


Page Documentation
==================
This stores all the information about a page. It takes an argument - the page's
name - then loads the page, renders it as reST, and gets all the metadata.

You'll need to write your pages in reStructuredText format. You'll also need to
specify an explicit page title - the first header in your file, if it has a
unique header style (I prefer for titles::

 =====
 Title
 =====

All other information will be gleaned from the file itself. The modification
time will be obtained from the file's timestamp and the URL will be based on the
file's name. If a file is in a directory, it can be accessed as ``parent/page``,
but you can't specify an index *inside* the directory, you'll need to have a
file in the root named ``parent.spp``.


Navbar File
===========
Navbars are stored in the ``navbar.ini`` file. They do not follow INI format,
instead, they use a special format.

To define the start of a new navbar, you can use either of::
    
    [navbar_name]
    [navbar_name : pages_must_start_with_this_to_display_it]

Then, for every link, you can use::
    
    Link Title: page_name_on_your_site
    External Link: http://this.is.an.example/
    Link On This Server: /feedback_mail.cgi


Template Context
================
    The template context consists of four elements.
    
``siteinfo`` : dict
    This is a dictionary of everything in the ``siteinfo`` block in your
    config file. It is generally recommended to have ``name`` and ``descr``
    in the config file.
``blocks`` : dict
    This is a dictionary of blocks. You must register the blocks in your
    config file, though.
``page`` : ``PageFile``
    This is an instance of PageFile. It has the attributes ``exists`` (which
    is False if this is a false page that only says "Page Not Found"),
    ``title`` (which is the page's title), ``content`` (which has been
    rendered to HTML already), ``mtime`` (a ``datetime.datetime`` object
    that represents the file's timestamp), and ``source`` (the reST source,
    which probably isn't useful).
``navbars`` : list
    This is a list of dictionaries. They have the keys ``title``, which is the
    title of the navbar, and ``links``, which is a list of similar dictionaries
    with the elements ``title`` and ``url``.


Example Template
================
::

 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
 <html>
  <head>
   <title>{{ siteinfo.name }} : {{ page.title }}</title>
  </head>
  <body>
   <div id="wrapper">
    <div id="header">
     <h1>{{ siteinfo.name }}</h1>
     <h3>{{ siteinfo.descr }}</h3>
    </div>
    <div id="subwrap">
     <div id="body">
      {{ page.content }}
     </div>
     <div id="nav">
     {%- for navbar in navbars -%}
      <div class="navbar">
      <h2>{{ navbar.title }}</h2>
      <ul>
       {%- for link in navbar.links -%}
       <li><a href="{{ link.url }}">{{ link.title }}</a></li>
       {%- endfor -%}
      </ul>
      </div>
     {%- endfor -%}
     </div>
    </div>
    <div id="footer">
     {{ blocks.footer }}
    </div>
   </div>
  </body>
 </html>
    
