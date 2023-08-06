from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='django-staticmedia',
    version='0.1',
    license='BSD',

    url='http://pypi.python.org/pypi/django-staticmedia',
    keywords='django utilities templatetag static media',
    description=(
        'Dynamically get URLs for your site-level and app-level static media.'
    ),

    author='Tamas Kemenczy',
    author_email='tamas.kemenczy@gmail.com',

    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
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
