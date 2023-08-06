from setuptools import setup, find_packages

setup(
    name="zc.lazylist",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'':'src'},
    install_requires=[
        'zope.testing'
    ],
    namespace_packages=['zc'],
    include_package_data=True,
    install_requirements = ['setuptools'],
    zip_safe = False
    )
