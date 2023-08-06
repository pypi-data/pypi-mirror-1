#/usr/bin/env python
"""
SweetPotatoPy
=============
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

That's about it. You'll also need to check these help files:

- ``read_home`` to lay out your directory,
- ``DOC_example_config_file`` to write a good config file,
- ``DOC_template_context`` to see what goes into a template,
- ``gen_navbar`` for info on writing your ``navbar.ini``, and
- ``FilePage`` to write the pages that go in your site.

:author:  LeafStorm/Pacific Science
:version: 1.0
:license: GNU General Public License
"""

import jinja2 as j
import ConfigParser
import datetime
from docutils.core import publish_parts
from pytin import *

global configfile
configfile = ConfigParser.ConfigParser()

global spp_request


### SECTION: FILE MANAGEMENT ###

global SPP_HOME_DIRECTORY

if __name__ == "__main__":
    # This is where you set your home directory for SPP.
    SPP_HOME_DIRECTORY = "/srv/spp" 
    # No trailing slash, please. Don't set this when prebaking.

def home(filename):
    return SPP_HOME_DIRECTORY + "/" + filename

def read_home(filename):
    """
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
    """
    try:
        return open(home(filename)).read()
    except:
        return None

def DOC_example_config_file():
    """
# ::
 
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
    """
    print DOC_example_config_file.__doc__



### SECTION: BLOCK PROCESSING ###

def getblocks():
    tempblocks = dict()
    for key, value in dict(configfile.items("blocks")).items():
        tempblocks[key] = publish_parts(read_home("blocks/" + value), writer_name='html')['html_body']
    return tempblocks



### SECTION: PAGE MANAGEMENT ###

class PageFile:
    """
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
    """
    def __init__(self, pagename):
        self.filename = home("pages/" + pagename + ".spp")
        self.pagename = pagename
        self.url = makelink(spp_request)
        try:
            self.file = open(self.filename)
            self.fileinfo = os.stat(self.filename)
            self.process_page()
            self.exists = True
        except IOError:
            self.title = "Page Not Found"
            self.content = "The page you requested doesn't exist."
            self.mtime = datetime.datetime.now()
            self.exists = False
            self.source = "The page you requested doesn't exist."

    def process_page(self):
        self.mtime = datetime.datetime.fromtimestamp(self.fileinfo.st_mtime)
        self.source = self.file.read()
        self.parts = publish_parts(self.source, writer_name='html')
        self.title = self.parts['title']
        self.content = self.parts['html_body']



### SECTION: NAVIGATION BAR ###
    
def gen_navbar(for_page):
    """
Navbars are stored in the ``navbar.ini`` file. They do not follow INI format,
instead, they use a special format.

To define the start of a new navbar, you can use either of::
    
    [navbar_name]
    [navbar_name : pages_must_start_with_this_to_display_it]

Then, for every link, you can use:
    
    Link Title: page_name_on_your_site
    External Link: http://this.is.an.example/
    Link On This Server: /feedback_mail.cgi
    """
    if not read_home("navbar.ini"):
        return None
    navbars = list()
    current = -1
    display = False
    for line in read_home("navbar.ini").splitlines():
        if line.startswith("[") and line.endswith("]"):
            navline = line.strip("[]").strip()
            if ":" in navline:
                if not for_page.startswith(navline.split(":")[1].strip()):
                    display = False
                else:
                    current += 1
                    navbars.append({'title': navline.split(":",)[0].strip(), 'links': list()})
                    display = True
            else:
                current += 1
                navbars.append({'title': navline.strip(), 'links': list()})
                display = True
        elif ":" in line:
            if display:
                navname = line.split(":", 1)[0].strip()
                navurl = line.split(":", 1)[1].strip()
                if navurl.startswith("http:") or navurl.startswith("/"):
                    navbars[current]['links'].append({'title': navname, 'url': navurl})
                else:
                    navbars[current]['links'].append({'title': navname, 'url': makelink(spp_request, path=navurl)})
    return navbars



### SECTION: SCRIPT RUNNING ###

def DOC_template_context():
    """
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
    """
    pass

def run(request):
    # Set the home directory and the config file
    #if 'home' in request.settings:
    global SPP_HOME_DIRECTORY
    SPP_HOME_DIRECTORY = request.settings['home']
    configfile.read(home("spp.ini"))
    
    # Set the response.
    global spp_request
    spp_request = request
    r = Response()
    
    # Get standard repeatable blocks from the config file.
    siteinfo = dict(configfile.items("siteinfo"))
    blocks = getblocks()
    
    # Prepare the page.
    if 'path' in spp_request.url:
        pagename = spp_request.url['path'].strip("/")
    else:
        pagename = configfile.get("navigation", "homepage")
    page = PageFile(pagename)
    
    # Get the navbar.
    navbar = gen_navbar(pagename)
    
    # Make the template environment.
    env = j.Environment(loader=j.FileSystemLoader(home("templates/" + 
        configfile.get("templating", "defaultdir"))))
    tpl = env.get_template(configfile.get("templating", "maintemplate"))
    
    # Assemble the context, finally.
    cxt = {'siteinfo': siteinfo, 
           'blocks': blocks,
           'page': page,
           'navbars': navbar}
    
    # Render and return the template.
    #r.ctype = 'text/plain'
    #r.wn(cxt)
    #r.wn(page.filename)
    r.wn(tpl.render(cxt))
    return r


if __name__ == "__main__": # in case prebakes aren't used
    bake(run, home=SPP_HOME_DIRECTORY)
