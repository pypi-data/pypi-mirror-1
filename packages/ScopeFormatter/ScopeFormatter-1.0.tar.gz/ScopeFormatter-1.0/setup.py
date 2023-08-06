try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

try:
    import scopeformatter
    doc_lines = scopeformatter.__doc__.strip().splitlines()
    description = doc_lines[0]
    long_description = '\n'.join(doc_lines[2:])
except ImportError:
    description = long_description = ''

setup(
    name='ScopeFormatter',
    version='1.0',
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
