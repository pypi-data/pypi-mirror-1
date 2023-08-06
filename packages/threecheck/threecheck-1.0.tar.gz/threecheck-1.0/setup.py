from distutils.core import setup
from distutils.cmd import Command
import subprocess, os, os.path

class RunTests(Command):
    description = "run the unittests of this package"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys
        sys.path.insert(0, 'src')
        try:
            from threecheck.tests import runAllTests
            runAllTests()
        finally:
            sys.path.pop(0)

class MakeDoc(Command):
    description = "make the documentation of this package"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        subprocess.check_call(args = ('make', 'html'),
            shell = False,
            cwd = os.path.join(
                os.path.dirname(__file__),
                'doc'))

setup(name = 'threecheck',
      version = '1.0',
      description = 'A typechecker for Python 3000',
      long_description = '''A typechecker for Python 3000, inspired by the `typechecker
        <http://oakwinter.com/code/typecheck/>`_ package. It provides about the
        same amount of feature: type checking of base and complex types, custom
        typecheckers, generator support, and more.''',
      author = 'Mattia Belletti',
      author_email = 'mattia.belletti@gmail.com',
      url = 'http://threecheck.sourceforge.net',
      classifiers = [
        "Programming Language :: Python :: 3.0",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"],
      license = "BSD License",
      platforms = "OS Independent",
      package_dir = {'': 'src'},
      packages = ['threecheck'],
      cmdclass = {'runtests': RunTests, 'doc': MakeDoc})
