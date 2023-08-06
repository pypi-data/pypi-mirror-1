from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='django-viewssi',
    version='0.1',
    license='BSD',

    url='http://pypi.python.org/pypi/django-viewssi',
    keywords='django utilities templatetag',
    description=(
        'Template tag for requesting views in templates (Django)'
    ),
    long_description=(
        'A template tag for making simulated GET requests '
        'to Django application view functions. The HTTP '
        'response can be displayed in the given template.'
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
