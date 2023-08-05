from setuptools import setup, find_packages

version = '0.1'

setup(name='cs.tags',
      version=version,
      description="",
      long_description=open('cs/tags/README.txt').read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='tag clouds tagging engine',
      author='CodeSyntax',
      author_email='fquintana@codesyntax.com',
      url='http://code.codesyntax.com/public/cs.tags',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
