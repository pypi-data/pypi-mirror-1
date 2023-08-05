from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='RhubarbTart',
      version=version,
      description="A light object publishing web framework built on WSGI and Paste",
      long_description="""\
RhubarbTart is a light object publishing web framework built on WSGI and Paste.

RhubarbTart is based on the CherryPy_ object publishing model. It is light and
simple, using WSGI_ components from Paste_ to compliment the object publishing
system with other features typical of a web framework

.. _CherryPy: http://cherrypy.org
.. _WSGI: http://python.org/peps/pep-0333.html
.. _Paste: http://pythonpaste.org

"Eternal happiness is Rhubarb Tart" -- Martin Heidegger `via Monty Python
<http://mzonline.com/bin/view/Python/RhubarbTartSong>`_

The latest version is available in a `Subversion repository
<http://svn.rhubarbtart.org/RhubarbTart/trunk/#egg=RhubarbTart-dev>`_.
""",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='wsgi web freamework',
      author='Julian Krause',
      author_email='thecrypto@thecrypto.org',
      url='http://rhubarbtart.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Paste==dev,>0.4.1'
          'PasteDeploy'
      ],
      entry_points="""
      [paste.paster_create_template]
      rhubarbtart=rhubarbtart.tart_template:RhubarbTart
      """,
      )
