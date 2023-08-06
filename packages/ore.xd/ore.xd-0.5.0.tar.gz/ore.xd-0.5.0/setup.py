from setuptools import setup, find_packages

setup(
    name="ore.xd",
    version="0.5.0",
    packages=find_packages('src', exclude=["*.tests"]),
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    install_requires = [ 'setuptools', 'dateutil'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },
    zip_safe=True,
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="""\
A Python XML Serializer/Deserializer that allows marshalling of simple types.

An XML Writer and an SAX Content Handler (XML Reader) are provided. 
""",
    license='ZPL',
    )
