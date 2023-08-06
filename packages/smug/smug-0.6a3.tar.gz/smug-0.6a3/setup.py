# See http://peak.telecommunity.com/DevCenter/setuptools for setuptools info.

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
from smug import VERSION

long_description = """Smug is a live-editing content system backed by a Git repository. It behaves like a wiki, except that the content is fully backed by a revision control system.
"""

setup(
    name='smug',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    requires=['django'],
    provides=['smug', 'gitlib'],
    author='Andrew McNabb',
    author_email='amcnabb@mcnabbs.org',
    url='http://www.mcnabbs.org/andrew/smug/',
    description='smugly superior to wikis',
    long_description=long_description,
    license='GNU GPLv3 or later',
    platforms=['linux', 'Apple OS X'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Version Control',
        'Topic :: Text Processing :: Markup',
        ]
    )
