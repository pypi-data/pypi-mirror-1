from setuptools import setup, find_packages

version = '0.3'

setup(
    name="Wareweb",
    version=version,
    description="A web framework; a next generation evolution from Webware/WebKit's servlet model",
    long_description="""\
This is a servlet-style web framework, similar to `Webware
<http://webwareforpython.org>`_, but both more minimal and more
convenient.
    
See also the `Subversion repository
<http://svn.pythonpaste.org/Paste/Wareweb/trunk#egg=Wareweb-dev>`_
""",
    classifiers=["Development Status :: 7 - Inactive",
                 "Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Python Software Foundation License",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Internet :: WWW/HTTP :: WSGI",
                 "Framework :: Paste",
                 ],
    keywords='web wsgi application framework',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/wareweb/",
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    zip_safe=True,
    install_requires=['Paste', 'PasteDeploy', 'PasteScript'],
    entry_points="""
    [paste.app_factory]
    main = wareweb.wsgiapp:make_wareweb_app

    [paste.paster_command]
    servlet = wareweb.servlet_script:ServletCommand

    [paste.paster_create_template]
    wareweb = wareweb.create_template:Wareweb
    """,
    )
