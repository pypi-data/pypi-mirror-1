from setuptools import setup

setup( name='servable',
       version='2009c',
       py_modules=['servable'],

       # metadata for upload to PyPI
       author = "Brandon Martin-Anderson/Nino Walker",
       author_email = "nino@urbanmapping.com",
       description = "Webservice mixin. Just subclass Servable, create your class, and transmute it into a webservice with the Servable-inherited 'wsgi_app' method. Plug that method into your favorite webserver, and go. If you don't have a favorite webserver, you can call 'run_test_server' on your Servable-derived class. That'll do in a pinch. ",
       license = "New BSD License",
       keywords = "web server webserver wsgi WSGI",
       url = "http://code.google.com/p/servable/",   
)
