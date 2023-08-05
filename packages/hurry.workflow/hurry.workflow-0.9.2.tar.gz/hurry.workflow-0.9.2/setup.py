import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'hurry', 'workflow', 'workflow.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

open('doc.txt', 'w').write(long_description)

setup(
    name="hurry.workflow",
    version="0.9.2",
    packages=find_packages('src'),
    
    package_dir= {'':'src'},
    
    namespace_packages=['hurry'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    author='Infrae',
    author_email='faassen@infrae.com',
    description="""\
hurry.workflow is a simple workflow system. It can be used to
implement stateful multi-version workflows for Zope 3 applications.
""",
    long_description=long_description,
    license='BSD',
    keywords="zope zope3",
    classifiers = ['Framework :: Zope3'],
    install_requires=['setuptools'],
    )
