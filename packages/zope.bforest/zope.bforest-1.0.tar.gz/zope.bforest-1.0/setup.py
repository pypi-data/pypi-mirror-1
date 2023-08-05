from setuptools import setup

setup(
    name="zope.bforest",
    version="1.0",
    license="ZPL 2.1",
    author="Zope Project",
    author_email="zope3-dev@zope.org",

    namespace_packages=["zope"],
    packages=["zope", "zope.bforest"],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["zope.interface", "ZODB3"],
    tests_require=["zope.testing"],
    description=open('README.txt').read(),
    long_description=open("src/zope/bforest/bforest.txt").read(),
    keywords="zope zope3",
    zip_safe=False
    )
