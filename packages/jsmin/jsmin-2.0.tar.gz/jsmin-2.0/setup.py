from setuptools import setup

import os
os.environ['COPYFILE_DISABLE'] = 'true'  # this disables including resource forks in tar files on os x

version = '2.0'


setup(
    name="jsmin",
    version=version,
    py_modules=['jsmin'],
    description='JavaScript minifier.',
    author='Dave St.Germain',
    author_email='dave@st.germa.in',
    test_suite='test.JsTests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Processing :: Filters',
    ],
)
