from setuptools import setup, find_packages

setup(
    name="zc.lazylist",
    version="0.1.1",
    packages=find_packages('src'),
    package_dir={'':'src'},
    install_requires=[
        'zope.testing',
        'setuptools',
    ],
    include_package_data=True,
    zip_safe = False
    )
