from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='django-svnlit',
    version='0.1',
    license='BSD',

    keywords='django subversion svn browser',
    description="Django-based subversion browser.",
    url='http://pypi.python.org/pypi/django-svnlit',

    author='Tamas Kemenczy',
    author_email='tamas.kemenczy@gmail.com',

    install_requires=(
        'pysvn',
    ),

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
