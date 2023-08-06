from setuptools import setup, find_packages
import sys, os

import batcher

def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()


setup(
    name='Batcher',
    version=batcher.__version__,
    description="Cut sliceable objects into batches, eg for paging display on a website",
    long_description=read('doc', 'index.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],

    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
