from setuptools import setup, find_packages

setup(
    name="zc.table",
    version="0.6",
    install_requires=['setuptools', 'zc.resourcelibrary >= 0.6'],
    packages=find_packages('src'),
    package_dir= {'':'src'},

    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.gif', '*.js'],
    'zc.table':['resources/*', '*.pt'],
    },

    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description=open("README.txt").read(),
    license='ZPL',
    keywords="zope zope3",
    zip_safe=False,
    classifiers = ['Framework :: Zope3'],
    )
