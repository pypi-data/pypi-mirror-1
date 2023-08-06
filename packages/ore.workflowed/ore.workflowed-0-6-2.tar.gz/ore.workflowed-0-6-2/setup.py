import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read().strip()

setup(
    name="ore.workflowed",
    version='0-6-2',
    url="http://bitbucket.org/kapilt/oreworkflowed",
    install_requires=['setuptools',
		      'zope.component',
                      'zope.event',
                      'zope.schema',
                      ],
    packages=find_packages(exclude=["*.tests"]),
    namespace_packages=['ore'],
    include_package_data = True,
    package_data = {
      '': ['*.txt', '*.zcml', '*.pt'],
    },
    zip_safe=False,
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="State Machine Workflow Engine",
    #long_description=read("ore","workflowed","readme.txt"),
    license='ZPL',
    keywords="workflow",
    )
