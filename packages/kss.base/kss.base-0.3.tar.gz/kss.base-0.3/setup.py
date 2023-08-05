from setuptools import setup, find_packages

version = '0.3'

long_description = """
KSS enables you write rich Ajax applications without having to code
Javascript. It does this by using a CSS like resource, this is called
a KSS file. All that you as a developer need to do is write files like
these and implement server side Python.

This Python package contains the Javascript engine and the server side
infrastructure. The package forms the base for ingegration with
specific web development frameworks. To see if there is support for
your framework go to the KSS website.
"""

setup(name='kss.base',
      version=version,
      description="KSS (Kinetic Style Sheets) framework",
      long_description=long_description,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='KSS Project',
      author_email='kss-devel@codespeak.net',
      url='http://kssproject.org',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'setuptools',
      ],

      entry_points={
        'kss.plugin': [
            'kss-core=kss.base.config:KSSCore'
            ],
        'console_scripts': [
            'ksspackage=kss.base.utils:ksspackage'
            ],
        },

      test_suite='kss.base.tests.test_suite',
)
