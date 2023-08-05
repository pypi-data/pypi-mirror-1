from setuptools import setup, find_packages

version = '0.3'

setup(name='XMLLayout',
      version=version,
      description="Formats Python log messages as log4j XMLLayout XML",
      long_description="""\
XMLLayout provides a Python logging Formatter that formats log messages as XML,
according to `log4j's XMLLayout specification
<http://jakarta.apache.org/log4j/docs/api/org/apache/log4j/xml/XMLLayout.html>`_.

XMLLayout formatted log messages can be viewed and filtered within the
`Chainsaw <http://logging.apache.org/log4j/docs/chainsaw.html>`_ application
(see the example section below), part of the Java based log4j project.

This package also includes a RawSocketHandler -- like
logging.handler.SocketHandler, but sends the raw log message over the socket
instead of a pickled version. RawSocketHandler can be configured to send log
messages to Chainsaw directly over a socket.

For example: to forward log messages to Chainsaw, if it were listening on
localhost port 4448::

    import logging
    import xmllayout
    
    handler = xmllayout.RawSocketHandler('localhost', 4448)
    handler.setFormatter(xmllayout.XMLLayout())
    logging.root.addHandler(handler)
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: System :: Logging'
        ],
      keywords='logging log4j',
      author='Philip Jenvey',
      author_email='pjenvey@groovie.org',
      url='http://pypi.python.org/pypi/XMLLayout',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      )
