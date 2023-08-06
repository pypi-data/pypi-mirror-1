import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-xsendfile',
    version = '1.0',
    url = 'http://toolpart.hu/code/download/django-xsendfile/',
    license = 'BSD',
    description = 'A Django application to serve files using xsendfile',
    long_description = read('README'),

    author = 'ToolPart Team LLC',
    author_email = 'toolpart@toolpart.hu',
    
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],

    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)

