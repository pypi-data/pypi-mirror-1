from setuptools import setup, find_packages

setup(
    name="ore.xapian",
    version="0.3.0",
    install_requires=['setuptools',
                      'xappy',
                      'zope.schema',
                      'zope.component',
                      'zope.lifecycleevent'],
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },
    zip_safe=True,
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="""\
An integration of Xapian Text Indexing for use with Zope3.""",
    license='GPL',
    keywords="zope zope3",
    )
