from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='django-virtualssi',
    version='1.0',
    license='BSD',

    url='http://pypi.python.org/pypi/django-virtualssi',
    description=(
        'Simulate Apache virtual server-side includes.'
    ),
    long_description=(
        'A template tag for making GET requests to the webserver. '
        'The HTTP response can be displayed in the given template. '
        'Use with the cache tag is recommended.'
    ),

    author='Tamas Kemenczy',
    author_email='tamas.kemenczy@gmail.com',

    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ),

    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=('ez_setup', 'examples', 'tests')),
)    
