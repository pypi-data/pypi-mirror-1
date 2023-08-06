from distutils.core import setup

setup(
    name='wget',
    version='0.2',
    author='anatoly techtonik <techtonik@gmail.com>',
    url='http://bitbucket.org/techtonik/python-wget/',

    description="python -m wget <URL>",
    license="Public Domain",
    classifiers=[
        'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],

    py_modules=['wget'],
)
