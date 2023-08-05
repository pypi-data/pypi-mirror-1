<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="installation", description="Installation", header="Setting Up"&>

    <&|doclib.myt:item, name="requirements", description="Requirements", &>
    <ul>
        <li>Python 2.3.3 or greater.  There is an issue with weakrefs (Python bug id <a href="http://sourceforge.net/tracker/?group_id=5470&atid=105470&func=detail&aid=839548">839548</a>) prior to that version which impacts stability.
        <li>For production webserver usage, a server environment that supports one of: CGI, WSGI, or mod_python.
        <li>For mod_python usage, Apache 1.3/mod_python 2.7 (or greater) or Apache 2.0/mod_python 3.1 (or greater).
        <li>Tested platforms:  Linux (RedHat 6.2, RedHat 9), Mac OSX, Solaris, Windows 2000.  Prefork and worker MPMs tested on Apache 2.0.
        <li>Familiarity with the webserver being used and whatever plug-in architecture being used.
    </ul>
    </&>

    <&|doclib.myt:item, name="quick", description="Quick Start - Running the Demo Server", &>
    <p>Myghty includes an out-of-the-box instant-gratification examples/documentation server you can run directly from the distribution files, which listens on port 8000 by default.  Extract the distribution from its .tar.gz file.  Then run the server as follows:</p>

    <&|formatting.myt:code, syntaxtype="cmd" &>
        cd /path/to/Myghty-X.XX/
        python ./tools/run_docs.py
    </&>

    <p>
    Then point a webbrowser to the location <span class="codeline"><a href="http://localhost:8000/">http://localhost:8000/</a>.</span>  An alternative port can be specified on the command line, e.g. <span class="codeline">python ./tools/run_docs.py 8100</span>.
    </p>
    <p>The demo server is a handy tool to browse through a release without having to perform an install.  The underlying HTTP server implementation can also be handy for development and prototyping.</p>
    </&>

    <&|doclib.myt:item, name="install", description="Installing the Library", &>
    
    <p>Myghty now installs with <a href="http://peak.telecommunity.com/DevCenter/setuptools">setuptools</a>, which is the next generation of the standard Python <span class="codeline">distutils</span> module.  Its basic usage is the same as that of distutils.  Switch to the user account under which Python is installed, and run:

        <&|formatting.myt:code, syntaxtype="cmd" &>
        cd /path/to/Myghty-X.XX/
        python setup.py install
        </&>

    As some systems may have multiple Python interpreters installed, be sure to use the Python executeable that corresponds to the Python being used by the webserver, such as the mod_python configuration, to insure the files go into the correct library path.  setup.py will precompile the Myghty .py files and install them in the library path for the Python executeable you just ran.  </p>
    
    <p>This installer also installs Myghty in a version-specific location, such as "site-packages/Myghty-0.99-py2.3.egg/".  If you have installed a version of Myghty prior to 0.99, the <span class="codeline">distutils</span>-based installation, which lives in "site-packages/myghty", will produce a conflict message when running setup.py.  After installation, you should delete the old install, either manually or via the command <span class="codeline">python ez_setup.py -D myghty</span>.
    </&>

    <&|doclib.myt:item, name="docgen", description="Generating the Documentation", &>

    <p>
    This documentation can also be generated into flat html files that are browseable directly from the filesystem.  Myghty can create these files by running the <span class="codeline">genhtml.py</span> utility:</p>

    <&|formatting.myt:code, syntaxtype="cmd" &>
    cd /path/to/Myghty-X.XX/doc
    python genhtml.py 
    </&>
    
    </&>
    <&|doclib.myt:item, name="paste", description="Running Paste Templates", &>
    <p>Myghty now includes a few <a href="http://www.pythonpaste.org">Python Paste</a> templates, which are pre-built Myghty applications that can install themselves into a runnable application.  Python 2.4 is required to run Python Paste.  </p>
    <p>Myghty's standard install procedure will automatically download and install all Python Paste components, which are also available at <a href="http://pythonpaste.org/download">http://pythonpaste.org/download</a>.  Also required is WSGIUtils, which must be installed from a particular .egg file format, via:</p>
    <&|formatting.myt:code, syntaxtype="cmd" &>
    python ez_setup.py http://pylons.groovie.org/files/WSGIUtils-0.6-py2.4.egg
    </&>
    
    <p>When Python Paste is installed, it will install the script "paster" into the standard Python scripts location.  Insure that this location is in your path.  Then to set up a Paste Template, just do:</p>
        <&|formatting.myt:code, syntaxtype="cmd" &>
        cd /target/directory
        paster create --template=myghty_simple myproject
        cd myproject
				paster serve server.conf
        </&>
    <p>The <span class="codeline">myghty_simple</span> template is a very small four-template configuration, which will by default listen on port 8080.  Also included is <span class="codeline">myghty_modulecomponent</span>, which shows off a more controller-oriented configuration, and <span class="codeline">myghty_routes</span>, which builds a new Rails-like "Routes" configuration. </p>
    
    <p>When a new Paste Template project is created, the file <span class="codeline"><%"<projectname>"|h%>/server.conf</span> illustrates the general Paste options, such as the server listening port.  Myghty-specific configuration information is in <span class="codeline"><%"<projectname>"|h%>/<%"<projectname>"|h%>/webconfig.py</span>.
    </p>
    </&>
    
    <&|doclib.myt:item, name="componentgen", description="Running Filesystem Components", &>
    
    <p>There is also a generic tool for running any Myghty template either to standard output or to a file.  The command is as follows:</p>

    <&|formatting.myt:code, syntaxtype="cmd" &>
    python tools/gen.py --help
    
    usage: gen.py [options] files...
    
    options:
      -h, --help            show this help message and exit
      --croot=COMPONENT_ROOT
                            set component root (default: ./)
      --dest=DESTINATION    set destination directory (default: ./)
      --stdout              send output to stdout
      --datadir=DATADIR     set data directory (default: dont use data directory)
      --ext=EXTENSION       file extension for output files (default: .html)
      --source              generate the source component to stdout
    </&>
    
    </&>
    
</&>


