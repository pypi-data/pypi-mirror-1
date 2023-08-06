from paver.defaults import Bunch

options(
    setup=Bunch(
        name="metamake",
        packages=['metamake'],
        license="BSD",
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
You will notice that whenever you run Metamake, a "Makefile" will be
created in your working directory that contains a bootstrapped version of
Metamake inside.  This allows anybody to build your project without needing
Metamake to be installed. With the bootstrapped Makefile, you can type
``make <args>`` to achieve the same effect as ``metamake <args>``.  Whenever you
update Metamake on your system, these bootstrapped Makefiles will be updated
automatically next time you execute Metamake for that project.  Commit these
Makefiles to your repository so that other people can check out your project
and build it without installing Metamake.

Easy Commandline Flag Definition
--------------------------------
Finally, Metamake allows you to define commandline flags that can be passed
into your application.  These flags will work regardless of whether you use
the 'metamake' tool or the bootstrapped Makefile::

    from metamake import task, shell, path, Flag

    Flag("cleanfirst").explain("set this flag to 'true' to do a clean build")

    @task
    def build()
        """builds the widget"""
        if Flag("cleanfirst").value is "true":
            clean()
        shell("qmake")

    @task
    def clean()
        """cleans the widget"""
        shell("rm -rf build")

When you execute ``metamake ls`` on the commandline, you will see these flags
listed underneath all of the task definitions, with the explanation that
you provided as documentation.

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

*NOTE:* in this example, build_cmd and clean_cmd are optional

''',
        version="1.0.0",
        author="Matt Pizzimenti",
        author_email="mjpizz+metamake@gmail.com",
        url="http://pypi.python.org/pypi/metamake/",
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
