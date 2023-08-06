from paver.defaults import Bunch

options(
    setup=Bunch(
        name="metamake",
        packages=['metamake'],
        version="1.0.5",
        license="BSD",
        author="Matt Pizzimenti",
        author_email="mjpizz+metamake@gmail.com",
        url="http://pypi.python.org/pypi/metamake/",
        description="Metamake is a dead-simple task-based automation tool written in Python.",
        long_description='''\
Description
===========

Metamake **is a simple way to define common tasks** and execute those tasks by
name, similar to Rake.  Metamake **is not** a dependency-tracking build tool
like Make, ant, qmake, SCons, Visual Studio, or XCode.  Metamake is used
**with** these build tools to orchestrate complex builds that work in a
cross-platform fashion.

Usage
=====
Using Metamake is as easy as creating a 'Makefile.py' in your project
directory::

    from metamake import task, shell, path

    @task
    def build()
        """builds the widget"""
        shell("qmake proj.pro -o Makefile.proj && make -f Makefile.proj")
        path("src/headers").copytree("dist/include")

On the commandline, you can then type ``metamake ls`` to see a listing
of all Metamake tasks defined in your Makefile.py, with their docstrings
helpfully listed to describe the purpose of that task.

Advanced Features
=================

Backwards-compatibility with Make
---------------------------------
To make things easier on newcomers to Metamake, a "Makefile" can be
created in your working directory that contains a bootstrapped version of
Metamake inside.  This allows anybody to build your project without needing
Metamake to be installed.  With the bootstrapped Makefile, you can type
``make <args>`` to achieve the same effect as ``metamake <args>``.  Whenever you
update Metamake on your system, these bootstrapped Makefiles will be updated
automatically next time you execute Metamake for that project.  You should 
commit these Makefiles to your repository so that other people can check out
your project and build it without installing Metamake.  To create a Makefile
bootstrap::

    from metamake import task, shell, bootstrap
    
    bootstrap("Makefile")
    
    # ...

What if you already have a Makefile that you are using for other purposes?
That's easy to solve, simply by specifying a different filename::
    
    from metamake import task, shell, bootstrap
    
    bootstrap("Makefile.meta")
    
    # ...
    
Easy Commandline Flag Definition
--------------------------------
Metamake allows you to define commandline flags that can be passed
into your build process.  These flags will work regardless of whether you use
the 'metamake' tool or the bootstrapped Makefile::

    from metamake import task, Flag

    Flag("cleanfirst").explain("set this flag to 'true' to do a clean build")
    
    if Flag("cleanfirst").given:
        print "flag was given"
    
    if Flag("cleanfirst").value == "true":
        print "flag value was True"

When you execute ``metamake ls`` on the commandline, you will see these flags
listed underneath all of the task definitions, with the explanation that
you provided as documentation.

From the first example, asking if the value is "true" or "false" is a bit unweildy
for a boolean value.  This gets even worse for flags that take a restricted set of
values, for example a range of integers.  The ``explain`` method can take a few
more parameters to help you out here::

    from metamake import task, Flag

    Flag("debuglevel").explain("set the debug level", convert=int, allow=[1,2,3,4])
    
    if Flag("debuglevel").value == 3:
        print "flag was converted to the integer 3"

You can also grab the Flag instance instead of always referring to the
string name::

    from metamake import task, Flag
    
    cleanflag = Flag("cleanfirst")
    debugflag = Flag("debuglevel")
    
    if cleanflag.given and debugflag.value == 3:
        print "we just checked the flag instances"
    

Readable, Cross-platform Filesystem Manipulation
------------------------------------------------
Jason Orendorff's excellent `path.py <http://pypi.python.org/pypi/path.py/>`_
library unifies all of the cross-platform Python filesystem manipulations
under a single object called **path**::

    from metamake import task, path

    @task
    def build():
        """builds the widget"""
        path("dist/include").makedirs()
        path("src/widget").copytree("dist/include/widget")
        for header_file in path("src/gadget").listdir("*.h"):
            header_file.copyfile("dist/include/gadget/%%s" %% header_file.basename())

Metamake extends Jason's library by providing console logging for file operations.
This makes it easy to see the manipulations that are happening to your filesystem
on the commandline.

External Dependency Tracking (alpha-quality)
--------------------------------------------
Metamake also supports the concept of Dependencies.  This allows you to specify
external dependencies for your project, without setting up messy hierarchical
builds using svn:externals or similar tools.  Every Dependency has three
methods:  ``update``, ``build``, and ``clean``::

    from metamake import task, shell, Dependency

    gadgetlib = Dependency(
        url = "svn://myrepo.com/gadgetlib",
        path = "~/.gadgetlib",
        build_cmd = "make",
        clean_cmd = "make clean",
    )

    @task
    def build()
        """builds the widget"""
        gadgetlib.update()
        gadgetlib.build()
        shell("qmake")
''',
        entry_points='''
[console_scripts]
mm = metamake:metamake_bin
metamake = metamake:metamake_bin
''',
        zip_safe = False,
        minilib=Bunch()
    )
)

@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
