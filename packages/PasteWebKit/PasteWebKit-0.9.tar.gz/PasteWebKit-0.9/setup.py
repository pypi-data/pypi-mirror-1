from setuptools import setup, find_packages

version = '0.9'

setup(
    name="PasteWebKit",
    version=version,
    description="A port/reimplementation of Webware WebKit in WSGI and Paste",
    long_description="""\
This is a reimplementation of the `Webware
<http://webwareforpython.org>`_ API, using `Paste
<http://pythonpaste.org>`_ for most of the functionality, and just
providing an API wrapper.

While the basic layout of applications is different from what
Webware's ``MakeAppWorkDir`` creates, this is intended to be backward
compatible for most typical Webware applications.
 
See also the `Subversion repository
<http://svn.pythonpaste.org/Paste/WebKit/trunk#egg=PasteWebKit-dev>`_
""",
    classifiers=[
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='web wsgi application framework webware webkit',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/webkit/",
    namespace_packages=['paste'],
    packages=find_packages(exclude='tests'),
    install_requires=['PasteDeploy', 'Paste', 'PasteScript'],
    zip_safe=False,
    package_data={
      'paste.webkit': ['paster_templates/*_tmpl',
                       'paster_templates/webkit/+project+.egg-info/*_tmpl',
                       'paster_templates/webkit/+package+/*_tmpl',
                       'paster_templates/webkit/+package+/web/*_tmpl',
                       ],
      },
    entry_points="""
    [paste.app_factory]
    main=paste.webkit.wsgiapp:make_webkit_app

    [paste.paster_command]
    servlet=paste.webkit.servlet_script:ServletCommand

    [paste.paster_create_template]
    webkit=paste.webkit.templates:WebKit
    """,
    )
