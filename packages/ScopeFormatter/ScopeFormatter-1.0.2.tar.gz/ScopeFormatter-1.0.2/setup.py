from __future__ import print_function
from distutils.core import setup
from doctest import testfile
import os.path as Path
import sys

readme_path = Path.join(Path.dirname(Path.abspath(__file__)), 'README.txt')

if __name__ == '__main__' and sys.argv[-1] == 'test':
    try:
        failure_count = testfile(readme_path, module_relative=False)[0]
    except IOError:
        print("The 'test' command requires README.txt.", file=sys.stderr)
        sys.exit(2)
    if failure_count == 0:
        print('All tests passed.')
        sys.exit()
    else:
        sys.exit(1)

try:
    import scopeformatter
    description = scopeformatter.__doc__.strip().splitlines()[0]
except ImportError:
    description = ''

try:
    long_description = open(readme_path).read()
except IOError:
    long_description = ''

setup(
    name='ScopeFormatter',
    version='1.0.2',
    license='MIT',
    author='Luke Stebbing',
    author_email='luke@lukestebbing.com',
    url='http://pypi.python.org/pypi/ScopeFormatter',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        ],
    description=description,
    long_description=long_description,
    py_modules=['scopeformatter'],
    )
