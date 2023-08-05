import os
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text

setup (
    name='gasp',
    version='0.4.0',
    author = "James Hancock",
    author_email = "jlhancock@gmail.com",
    description = "Graphics API for Students of Python",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('CHANGES.txt')
        ),
    license = "GPL2",
    keywords = "gasp pygame graphics education",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Education :: Computer Aided Instruction (CAI)'],
    url = 'http://dc.ubuntu-us.org/bazaar/gasp',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    extras_require = dict(
        test = ['zope.testing'],
        ),
    install_requires = [
        #'pygame',
        'setuptools',
        ],
    zip_safe = False,
    )
