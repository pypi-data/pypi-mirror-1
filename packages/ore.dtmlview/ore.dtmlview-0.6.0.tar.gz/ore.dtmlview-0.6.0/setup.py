
from setuptools import setup, find_packages

setup(
    name="ore.dtmlview",
    version="0.6.0",
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.js', '*.dtml'],
    },
    zip_safe=False,
    author='ObjectRealms, LLC',
    author_email='info@objectrealms.net',
    description="classic DTML useable as Zope3",
    long_description="""\
Allows for the use of Document Template Markup Language (DTML) in the construction of
Zope3 View, in manner similiar to Page Templates. Benefits over the latter are the generation
of non xml/xhtml output like javascript.
""",
    license='ZPL',
    keywords="zope zope3",
    )
