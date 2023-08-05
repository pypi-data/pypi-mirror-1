from setuptools import setup

name = "erp5flakes"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Jerome Perrin",
    author_email = "jerome@nexedi.com",
    description =
      "A wrapper around pyflakes for ERP5 Products and Business Templates",
    long_description = file('README.txt').read(),
    license = "GPL 2",
    keywords = "erp5 zope2 pyflakes",
    url = 'https://svn.erp5.org/repos/public/erp5/trunk/utils/%s' % name,
    classifiers = [
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Framework :: Zope2",
      "Programming Language :: Python",
      ],
    scripts = ["bin/erp5flakes"],
    install_requires = ['pyflakes', ], # ZODB, ERP5Type
  )

