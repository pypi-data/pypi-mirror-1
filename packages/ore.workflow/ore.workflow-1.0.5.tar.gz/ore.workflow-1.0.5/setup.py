from setuptools import setup, find_packages

setup(
    name="ore.workflow",
    version="1.0.5",
    packages=find_packages('src'),
    package_dir= {'':'src'},
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    author='Zope 3 Community',
    author_email='kapil.foss@gmail.com',
    description="workflow engine for zope3",
    long_description="""\
ore.workflow is a simple workflow system. It allows for stateful multi-version
workflows for Zope3 applications based on adaptation, and supports parallel
workflows on a single context. Its based on hurry.workflow, and adds adapation, 
and parallel workflows.
""",
    license='BSD',
    keywords="zope zope3",
    classifiers = ['Framework :: Zope3'],
    install_requires=['setuptools', 
                      'zope.annotation',
                      'zope.component',	
                      'zope.event',	
                      'zope.security',
                      ],
    )
