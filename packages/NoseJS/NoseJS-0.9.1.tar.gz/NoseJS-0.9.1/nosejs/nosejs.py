
import os
import subprocess
from nose.plugins.base import Plugin
from nose.config import ConfigError
import logging

log = logging.getLogger('nose.plugins.nosejs')

resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

def get_resource(filename):
    return os.path.join(resource_dir, filename)

class NoseJS(Plugin):
    """Runs JavaScript tests using Rhino for Java in a subprocess."""
    name = 'javascript'
    
    def options(self, parser, env=os.environ):
        Plugin.options(self, parser, env)
        parser.add_option('--java-bin', default="java", help=(
            "Path to java executable.  Default: %default (using $PATH)"
        ))
        parser.add_option('--rhino-jar', help=(
            "Path to rhino1_7R1/js.jar (or later release). Download from http://www.mozilla.org/rhino/"
        ))
        parser.add_option('--rhino-jar-no-debug', dest='rhino_jar_debug', 
            action='store_false', default=True, help=(
            "Do not pass the -debug flag to js.jar.  By default -debug is passed because "
            "it shows tracebacks."
        ))
        parser.add_option('--with-dom', action="store_true", help=(
            "Simulate the DOM by loading John Resig's env.js "
            "before any other JavaScript files."
        ))
        parser.add_option('--load-js-lib', dest='javascript_libs_to_load', 
            action='append', metavar='FILEPATH', default=[], help=(
            "Path to a JavaScript file that should be loaded before the tests. "
            "This option can be specified multiple times."
        ))
        parser.add_option('--js-test-dir', dest='javascript_test_dirs', 
            action='append', metavar='FILEPATH', default=[], help=(
            "Path to where JavaScript tests live.  Must be a subdirectory of where "
            "Nose is already looking for tests (i.e. os.getcwd()).  "
            "This option can be specified multiple times."
        ))
        possible_res = []
        os.walk(resource_dir)
        for root, dirs, files in os.walk(resource_dir):
            for name in files:
                if name[0] in ('.','_'):
                    continue
                if name.find('README') != -1:
                    continue
                abspath = os.path.join(root, name)
                possible_res.append(abspath.replace(resource_dir+"/", ""))
            
        parser.add_option('--load-js-resource', dest='resources_to_load', 
            action='append', metavar='RELATIVE_FILEPATH', help=(
            "Relative path to internal nosejs resource file that should be loaded before tests "
            "(but after DOM initialization).  This option can be specified multiple times.  "
            "Possible values: %s" % ", ".join(possible_res)
        ))
        runner = get_resource('rhino-testrunner.js')
        if not os.path.exists(runner):
            runner = None
        parser.add_option('--rhino-testrunner', metavar="RHINO_TESTRUNNER", default=runner, help=(
            "JavaScript that runs tests in Rhino.  When test files are discovered they will be executed as "
            "java -jar rhino1_7R1/js.jar RHINO_TESTRUNNER <discovered_test_file>.  "
            "Default: %default"
        ))
        parser.add_option('--nosejs-work-dir', help=(
            "A path to change into before running any commands"
        ))

    def configure(self, options, config):
        Plugin.configure(self, options, config)
        self.files = []
        if not options.rhino_jar:
            raise ConfigError("--rhino-jar (path to js.jar) must be specified")
        wd = options.nosejs_work_dir
        if not wd:
            wd = os.getcwd()
        if not os.path.exists(os.path.join(wd, options.rhino_jar)):
            raise ConfigError("Rhino js.jar does not exist: %s" % options.rhino_jar)
        if not options.rhino_testrunner:
            raise ConfigError("--rhino-testrunner (JavaScript test runner) must be specified")
        if not os.path.exists(os.path.join(wd, options.rhino_testrunner)):
            raise ConfigError("%s: file does not exist" % options.rhino_testrunner)
        
        libs = [get_resource('__nosejs__.js')] # load the runtime first
        if options.with_dom:
            libs.append(get_resource('env.js'))
            # load this HTML file so that the DOM gets activated:
            libs.append(get_resource('__nosejs__.html'))
        if options.resources_to_load:
            for resource in options.resources_to_load:
                libs.append(get_resource(resource))
        libs.extend(options.javascript_libs_to_load)
        options.javascript_libs_to_load = libs
        
        # explode --js-test-dir values into incremental paths
        # that can be used by wantDirectory() to descend into the 
        # actual path.  
        #
        # I.E. --js-test-dir=/path/to/somewhere/else/ becomes:
        #   /path/
        #   /path/to/
        #   /path/to/somewhere/
        #   /path/to/somewhere/else/
        
        self.javascript_test_dirs = set([])
        root = os.getcwd()
        for dir in options.javascript_test_dirs:
            absdir = os.path.abspath(dir)
            # fixme: look for non working dir nose starting points?
            if not absdir.startswith(root):
                raise ValueError(
                    "Option --js-test-dir=%s must be somewhere along the working directory "
                    "path (currently %s)" % (absdir, root))
            absdir = absdir.replace(root, '')
            parts = absdir.split(os.sep)
            for i in range(len(parts)):
                incremental_part = os.sep.join(parts[0:i])
                if incremental_part:
                    if incremental_part.startswith(os.sep):
                        incremental_part = incremental_part[len(os.sep):]
                    self.javascript_test_dirs.add(os.path.join(root, incremental_part))
        log.debug("Exploded --js-test-dir(s): %s" % self.javascript_test_dirs)
        
        self.options = options
    
    def wantDirectory(self, dirpath):
        want_dir = dirpath in self.javascript_test_dirs
        log.debug("Want directory: %s ? %s" % (dirpath, want_dir))
        if want_dir:
            return True
        return None
    
    def wantFile(self, file):
        # fixme: provide custom extensions?
        if file.endswith('.js'):
            # fixme: provide custom test matches?
            if self.conf.testMatch.search(os.path.basename(file)):
                # just store it, don't return True
                log.debug("Storing file: %s" % file)
                self.files.append(file)
            
        return None
        
    def report(self, stream):
        print >> stream, "----------------------------------------------------------------------"
        cmd = [self.options.java_bin, '-jar', self.options.rhino_jar] 
        if self.options.rhino_jar_debug:
            cmd.append('-debug')
        cmd.append(self.options.rhino_testrunner)
        for js_lib in self.options.javascript_libs_to_load:
            cmd.append(js_lib)
        cmd.extend(self.files)
        log.debug("command to run is: \n  %s\n" % "\n    ".join(cmd))
        p = subprocess.Popen(
            cmd, env={'PATH':os.environ.get('PATH',None)},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=self.options.nosejs_work_dir
        )
        stream.write(p.stdout.read())
        returncode = p.wait()
        print >> stream, ""
        if returncode != 0:
            # fixme: need to tell nose to exit non-zero
            print >> stream, "FAIL"
        else:
            print >> stream, "OK"
            