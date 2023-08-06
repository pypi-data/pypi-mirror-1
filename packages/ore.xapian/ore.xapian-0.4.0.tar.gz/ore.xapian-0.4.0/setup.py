import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    
setup(
    name="ore.xapian",
    version="0.4.0",
    install_requires=['setuptools',
                      'xappy',
                      'transaction',
                      'zope.schema',
                      'zope.component',
                      'zope.lifecycleevent'],
    packages=find_packages('src'),
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },
    zip_safe=True,
    classifiers = [
        'Intended Audience :: Developers',
        'Framework :: Zope3'
        ],
    url="http://pypi.python.org/pypi/ore.xapian",
    keywords="zope3 index search xapian xappy",
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="An Content Indexing/Searching Framework for use with Zope3, built on Xapian",
    long_description=(
        read('src','ore','xapian','readme.txt')
        + '\n\n' +
        read('changes.txt')
        + '\n\n'
        ),
    license='GPL',
    keywords="zope zope3",
    )
