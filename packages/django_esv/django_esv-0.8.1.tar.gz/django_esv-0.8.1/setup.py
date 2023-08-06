import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(
    name = "django_esv",
    version = "0.8.1",
    url = 'http://github.com/mintchaos/django_es',
    license = 'BSD',
    description = "A django_inlines style inline and a template tag to work with the ESV Bible API.",
    long_description=README,

    author = 'Christian Metts',
    author_email = 'xian@mintchaos.com',
    packages = [
        'esv',
        'esv.templatetags',
    ],
    install_requires = ['httplib2'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
