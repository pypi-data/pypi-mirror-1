from setuptools import setup, find_packages
import sys, os

version = '0.1a9'


install_requires=[]
if sys.version_info[:2] < (2,6):
    install_requires.append("simplejson")


setup(
    name='WebFlash',
    version=version,
    description="Portable flash messages for WSGI apps",
    long_description="",
    keywords='wsgi flash webob',
    author='Alberto Valverde Gonzalez',
    author_email='alberto@python-rum.org',
    url='http://python-rum.org/wiki/WebFlash',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=["WebTest", "nose"],
    test_suite="nose.collector",
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
