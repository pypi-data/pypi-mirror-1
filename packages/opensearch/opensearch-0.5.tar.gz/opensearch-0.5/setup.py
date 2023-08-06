# bootstrap easy_install
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

classifiers = """\
Intended Audience :: Education
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Text Processing :: General
"""

setup( 
    name             = 'opensearch',
    version          = '0.5',
    url              = 'http://python.org/pypi/opensearch',
    download_url     = 'http://inkdroid.org/bzr/opensearch',
    author           = 'Ed Summers',
    author_email     = 'ehs@pobox.com',
    license          = 'http://www.opensource.org/licenses/gpl-license.php',
    packages         = [ 'opensearch' ],
    description      = "Interact with opensearch services",
    classifiers      = filter( None, classifiers.split("\n") ),
    test_suite       = 'test',
)

