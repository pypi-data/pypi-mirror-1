from setuptools import setup, find_packages

version = '0.5.1'

setup(name='tramline',
      version=version,
      description=("An easy and fast upload and download accelerator "
                   "for application servers."),
      long_description="""\
Tramline is a upload and download accelerator that plugs into Apache,
using mod_python. Its aim is to make downloading and uploading large
media to an application server easy and fast, without overloading the
application server with large amounts of binary data.

Tramline integrates into Apache using mod_python. The application
server is assumed to sit behind Apache, for instance hooked up using
mod_proxy or mod_rewrite.

Tramline takes over uploading and downloading files, handling these
within Apache. Only a small configuration change in Apache should be
necessary to enable tramline.

The application server remains in complete control over security, page
and form rendering, and everything else. Minimal changes are necessary
to any application to enable it to work with tramline; in fact it's
just setting two response headers in a few places in the code.
""",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        ],
      keywords='web zope command-line skeleton project',
      author='Martijn Faassen',
      author_email='faassen@infrae.com',
      url='http://www.infrae.com/products/tramline',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      zip_safe=False,
      )
