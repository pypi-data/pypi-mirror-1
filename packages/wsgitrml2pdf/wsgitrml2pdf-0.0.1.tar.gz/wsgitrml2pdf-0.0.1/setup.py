from setuptools import setup

__author__ = "Atsushi Odagiri"
__version__ = "0.0.1"

setup(
    name="wsgitrml2pdf",
    version=__version__,
    author=__author__,
    author_email="aodagx@gmail.com",
    url="http://bitbucket.org/aodag/wsgitrml2pdf/",
    description="""\
wsgitrml2pdf is wsgi middleware to convert trml text to pdf.
inspired by `django_trml2pdf <http://pypi.python.org/pypi/django_trml2pdf/>`_.

It uses `trml2pdf <http://pypi.python.org/pypi/trml2pdf>`_ and `reportlab <http://ppi.python.org/pypi/reportlab>`_.

use middleware::

 from webob.dec import wsgify
 from wsgitrml2pdf import make_middleware

 @wsgify
 def application(req):
     return Response(body=open("hello.trml").read(), content_type="x-application/trml")

 app = make_middleware(application, content_type="x-application/trml")


    """,
    license="LGPL",
    install_requires=[
        "WebOb",
        "reportlab",
        #"trml2pdf",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Text Processing :: Markup",
    ],
)

