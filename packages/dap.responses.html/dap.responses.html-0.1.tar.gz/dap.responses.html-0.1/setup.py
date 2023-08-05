# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1'

setup(name='dap.responses.html',
      version=version,
      description="Simple HTML form for pydap server",
      long_description="""\
This is a simple HTML response, building a form to download data
in ASCII format. The response builds the HTML page and redirects
the user to the ASCII response when a POST is done.

Even though pydap uses Cheetah for templating, I decided to use a
templating engine called ``templess`` for this response. Templess
is lightweight (~25k) and fun to work with, justifying the choice.

A nice thing about the response is that the redirection to the ASCII
response and the error message when no variable is selected are
both done by raising exceptions. These exceptions are *not* captured
by the server, that allows them to be captured by the Paste#httpexceptions
middleware.

If you use this response, don't forget to edit the template file
and add a link pointing to the HTML response when clicking a filename.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/responses/html#egg=dap.responses.html-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='html dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/responses/html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.responses'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'dap[server]>=2.2.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.response]
      html = dap.responses.html
      """,
      )
      
