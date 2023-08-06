from StringIO import StringIO
from zlib import compress, decompress
from base64 import b64encode, b64decode
from inspect import getsource
from tempfile import gettempdir
import metamake
from metamake._path import path, path

def serialize_metamake_to_makefile(makefile_filename):
    """given a filename for a makefile, serializes all information
    necessary to that makefile to bootstrap metamake into memory
    and run a Makefile.py"""
    
    # if there is an old makefile, keep the contents in case
    # we need to revert
    if path(makefile_filename).exists():
        old_makefile_file = open(makefile_filename, "r")
        try:
            old_makefile_file_contents = old_makefile_file.read()
            
            # check the version, don't clobber newer metamake versions
            try:
                version_line = old_makefile_file_contents.split("\n")[0]
                if "metamake" in version_line:
                    old_makefile_metamake_version = version_line[11:].strip()
                    if old_makefile_metamake_version > metamake.__version__:
                        # skip this bootstrapping altogether when this version is older
                        return
            except:
                # something was wrong with the version number, assume it is out of date
                pass
            
        finally:
            old_makefile_file.close()
    else:
        old_makefile_file_contents = None
    
    # open the makefile file for writing the serialized code
    new_makefile_file = open(makefile_filename, "w")
    
    # write the version number
    new_makefile_file.write("# metamake %s\n" % metamake.__version__)
    
    try:
        
        # get the metamake module directory
        metamake_dir = path(__file__).dirname()
        
        # iterate over all python files in the module directory
        for python_filename in metamake_dir.listdir("*.py"):
        
            # get the file contents
            raw_contents = open(python_filename).read()
        
            # b64 encode it so that it goes nicely in a one-liner comment
            serialized_contents = b64encode(compress(raw_contents))
        
            # write it out to the makefile
            python_filebasename = python_filename.basename()
            new_makefile_file.write("# %(python_filebasename)s %(serialized_contents)s\n" % locals())
        
    except Exception, e:
        
        new_makefile_file.close()
        
        if old_makefile_file_contents:
            
            # we had an old makefile, revert to it
            reverted_makefile_file = open(makefile_filename)
            try:
                reverted_makefile_file.write(old_makefile_file_contents)
            finally:
                reverted_makefile_file.close()
        else:
            
            # there was no makefile here before, remove the bad one
            path(makefile_filename).remove()
    
    # write the deserialization code into default make targets
    sourcecode = getsource(standalone_deserialize_metamake_from_makefile.func_code)
    oneliner = ";".join([
        "from base64 import b64decode",
        "from imp import load_source",
        "from tempfile import TemporaryFile, gettempdir",
        "tempcodefile = TemporaryFile()",
        "tempcodefile.write(b64decode('%s'))" % b64encode(sourcecode),
        "tempcodefile.seek(0)",
        "makefile_metamake_bootstrapper = load_source('makefile_metamake_bootstrapper', gettempdir(), tempcodefile)",
        "makefile_metamake_bootstrapper.standalone_deserialize_metamake_from_makefile('%s')" % makefile_filename,
    ])
    
    new_makefile_file.write('''
BOOTSTRAPMETAMAKE=%(oneliner)s

__default:
	@python -c "$(BOOTSTRAPMETAMAKE);import sys;import os;sys.path.insert(0, os.getcwd());import Makefile;import metamake;metamake.run_default_task();"

ls:
	@python -c "$(BOOTSTRAPMETAMAKE);import sys;import os;sys.path.insert(0, os.getcwd());import Makefile;import metamake;metamake.list_tasks()"

%%:
	@python -c "$(BOOTSTRAPMETAMAKE);import sys;import os;sys.path.insert(0, os.getcwd());import Makefile;import metamake;metamake.run_task('$@', from_makefile=True)"
''' % locals())
    
    # we are done serializing, close the makefile
    new_makefile_file.close()

def standalone_deserialize_metamake_from_makefile(makefile_filename):
    """internal helper definition. deserializes metamake from a makefile
    and places it in the system temp directory (e.g.
    /tmp/metamake_bootstrap/metamake).  It *must* import all of its own
    dependencies since it will be serialized into its own file"""
    
    import sys
    import os
    import os.path
    from zlib import decompress
    from base64 import b64decode
    from tempfile import gettempdir
    
    # set up a path for the metamake
    temp_metamake_import_path = os.path.join(gettempdir(), "metamake_bootstrap")
    temp_metamake_module_path = os.path.join(temp_metamake_import_path, "metamake")
    if not os.path.exists(temp_metamake_import_path):
        os.mkdir(temp_metamake_import_path)
    if not os.path.exists(temp_metamake_module_path):
        os.mkdir(temp_metamake_module_path)
    
    # read the commented lines from the makefile
    makefile_file = open(makefile_filename)
    makefile_lines = []
    try:
        makefile_lines = [line.replace("# ","") for line in makefile_file.readlines() if line.startswith("#") and not line.startswith("# metamake")]
    finally:
        makefile_file.close()
    
    # each line contains the contents of a file, dump them into metamake_bootstrap/metamake
    for line in makefile_lines:
        metamake_subfilename, serialized_source = line.split(" ", 1)
        full_subfile_path_in_temp = os.path.join(temp_metamake_module_path, metamake_subfilename)
        subfile = open(full_subfile_path_in_temp, "w")
        try:
            deserialized_code = decompress(b64decode(serialized_source))
            subfile.write(deserialized_code)
        finally:
            subfile.close()
    
    # add the temp import dir to the system path
    sys.path.insert(0, temp_metamake_import_path)
