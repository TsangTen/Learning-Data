from setuptools import setup


setup(
    name='flaskr',
    packages=['flaskr'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    setup_requires=[  # One way to handle testing is to integrate it with setuptools.
        'pytest-runner',  # Here that requires adding a couple of lines to the setup.py file
    ],  # and creating a new file setup.cfg.
    tests_require=[  # One benefit of running the tests this way is that you do not have to install pytest.
        'pytest',
    ],
)

"""
When using setuptools, 
it is also necessary to specify any special files 
that should be included in your package (in the MANIFEST.in). 
In this case, 
the static and templates directories need to be included, 
as well as the schema.
"""


"""
This calls on the alias created in setup.cfg which in turn runs pytest via pytest-runner, 
as the setup.py script has been called. (Recall the setup_requires argument in setup.py) 
Following the standard rules of test-discovery your tests will be found, run, and hopefully pass.
"""

"""
This is one possible way to run and manage testing. Here pytest is used, 
but there are other options such as nose. 
Integrating testing with setuptools is convenient 
because it is not necessary to actually download pytest 
or any other testing framework one might use.
"""
