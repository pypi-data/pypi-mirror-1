from setuptools import setup

setup(name="cgi.unescape",
    version="0.0.2",
    url='http://pypi.python.org/pypi/cgi.unescape',
    description="back replace html-safe sequences to special characters",
    keywords="html xml sgml escape unescape quote unquote cgi www web xhtml",
    namespace_packages=["cgi"],
    packages=["cgi"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ], 
    zip_safe=True,
    long_description="""
::
  
  >>> cgi.unescape('&lt; &amp; &gt;')
  '< & >'
  >>> unescape('&#39;')
  "'"
  >>> unescape('&#x27;')
  "'"
				
full list of sequences: htmlentitydefs.entitydefs""",
)
