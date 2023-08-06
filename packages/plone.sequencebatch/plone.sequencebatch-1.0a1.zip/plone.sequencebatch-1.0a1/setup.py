from setuptools import setup, find_packages

version = '1.0a1'

setup(
    name='plone.sequencebatch',
    version=version,
    description="Facilities for creating a batched sequence.",
    long_description=open("README.txt").read() + "\n" +
                     open("CHANGES.txt").read(),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Zope2',
    ],
    keywords='Plone',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://pypi.python.org/pypi/plone.sequencebatch',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'ExtensionClass',
        'Zope2',
    ],
)
