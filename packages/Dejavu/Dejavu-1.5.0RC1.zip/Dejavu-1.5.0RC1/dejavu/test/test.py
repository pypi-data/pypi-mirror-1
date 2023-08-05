import getopt
import sys
import unittest

from dejavu.test import tools


class djvTestHarness(object):
    """A test harness for Dejavu."""
    
    def __init__(self, available_tests):
        """Constructor to populate the TestHarness instance.
        
        available_tests should be a list of module names (strings).
        """
        self.available_tests = available_tests
        self.tests = []
    
    def load(self, args=sys.argv[1:]):
        """Populate a TestHarness from sys.argv.
        
        args defaults to sys.argv[1:], but you can provide a different
            set of args if you like.
        """
        
        longopts = ['help']
        longopts.extend(self.available_tests)
        try:
            opts, args = getopt.getopt(args, "", longopts)
        except getopt.GetoptError:
            # print help information and exit
            self.help()
            sys.exit(2)
        
        self.tests = []
        
        for o, a in opts:
            if o == '--help':
                self.help()
                sys.exit()
            else:
                o = o[2:]
                if o in self.available_tests and o not in self.tests:
                    self.tests.append(o)
        
        if not self.tests:
            self.tests = self.available_tests[:]
    
    def help(self):
        """Print help for test.py command-line options."""
        
        print """
Dejavu Test Program
    Usage:
        test.py --<testname>
        
        tests:"""
        for name in self.available_tests:
            print '        --' + name
    
    def run(self, conf=None):
        """Run the test harness."""
        self.load()
        
        import dejavu
        print "Python version:", sys.version.split()[0]
        print "Dejavu version:", dejavu.__version__
        
        for testmod in self.tests:
            if testmod.startswith("test_store"):
                print
                print "Testing %s storage..." % testmod[10:]
                mod = __import__(testmod, globals(), locals(), [''])
                if hasattr(mod, 'proxied_opts'):
                    mod.proxied_opts['Prefix'] = 'test'
                elif hasattr(mod, 'opts'):
                    mod.opts['Prefix'] = 'test'
                mod.run()
            else:
                suite = unittest.TestLoader().loadTestsFromName(testmod)
                tools.djvTestRunner.run(suite)


def run():
    
    tools.prefer_parent_path()
    
    testList = [
        'test_analysis',
        'test_codewalk',
        'test_containers',
        'test_dejavu',
        'test_logic',
        'test_storeram',
        'test_storeburned',
        'test_storecaching',
        'test_storefs',
        'test_storefirebird',
        'test_storemsaccess',
        'test_storemysql',
        'test_storeproxy',
        'test_storepsycopg',
        'test_storepypgsql',
        'test_storeshelve',
        'test_storesqlite',
        'test_storesqlserver',
    ]
    djvTestHarness(testList).run()


if __name__ == '__main__':
    run()
