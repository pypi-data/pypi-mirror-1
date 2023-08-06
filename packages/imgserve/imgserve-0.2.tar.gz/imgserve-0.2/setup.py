import os
from imgserve import version
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read_file(name):
    return open(os.path.join(os.path.dirname(__file__),name)).read()


config = {
    'name': version.NAME,
    'version': version.VERSION['version'],
    'description': 'Imgserve is a daemon program to provide common image processing service',
    'long_description': read_file('README'),
    'author': 'Wu Zhe',
    'author_email': 'wu@madk.org',
    'url': 'http://github.com/wuzhe/imgserve',
    'download_url': 'http://pypi.python.org/pypi/imgserve',
    'license': 'GPL',
    'package_data': {'imgserve': ['arial.ttf']},
    'scripts': ['bin/imgserve'],
    'install_requires': [
        'setuptools',
        'python-daemon',
        'simplejson',
        'cogen>=0.2.1',
        ],
    'tests_require': [
        'pyftpdlib',
        ],
    'packages': ['imgserve'],
    'keywords': 'image-processing daemon networking imgserve',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Utilities',
        ],
    }

setup(**config)
