# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt


from setuptools import setup, find_packages

setup(
    name='gocept.devtools',
    version = '0.4',
    author='Christian Theune',
    author_email='ct@gocept.com',
    description='Small utilities for managing code.',
    packages=find_packages('.'),
    package_dir = {'': '.'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
        ],
    entry_points="""
        [console_scripts]
        fix-copyright = gocept.devtools.copyright:main
    """)
