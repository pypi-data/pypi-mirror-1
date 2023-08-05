from distutils.core import setup

setup(
        # Package metadata.
        name='pep362',
        version='0.4',
        description='Implementation of PEP 362 (Function Signature objects)',
        author='Brett Cannon',
        author_email='brett@python.org',
        url='http://svn.python.org/view/sandbox/trunk/pep362/',
        # Files.
        py_modules=['pep362'],
        data_files=['README'],
    )
