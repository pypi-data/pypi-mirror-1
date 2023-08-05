from setuptools import setup

__version__ = '0.4'

setup(name="ZPTKit",
      version=__version__,
      description="Tool to use Zope Page Templates with Webware or Paste",
      long_description="""\
ZPTKit provides tools for using Zope Page Templates in Webware or
Paste.  Additionally, tools for building templated emails (with text
alternative) are included.
""",
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Topic :: Text Processing :: Markup :: HTML",
                   ],
      author="Ian Bicking",
      author_email="ianb@imagescape.com",
      url="http://imagescape.com/software/ZPTKit/",
      license="MIT",
      packages=["ZPTKit", "ZPTKit.backports"],
      include_package_data=True,
      install_requires=['ZopePageTemplates', 'Component'],
      entry_points="""
      [paste.paster_create_template]
      zpt=ZPTKit.paster_templates:ZPT
      """,
      )
