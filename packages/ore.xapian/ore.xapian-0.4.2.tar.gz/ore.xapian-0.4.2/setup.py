import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    
setup(
    name="ore.xapian",
    version="0.4.2",
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
    zip_safe=False,
    classifiers = [
        'Intended Audience :: Developers',
        'Framework :: Zope3'
        ],
    url="https://svn.objectrealms.net/svn/public/ore.xapian/",
    keywords="zope3 index search xapian xappy",
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="A Xapian Content Indexing/Searching Framework for Zope3",
    long_description=(
        read('src','ore','xapian','readme.txt')
        + '\n\n' +
        read('changes.txt')
        + '\n\n'
        ),
    license='GPL',
    keywords="zope zope3",
    )
