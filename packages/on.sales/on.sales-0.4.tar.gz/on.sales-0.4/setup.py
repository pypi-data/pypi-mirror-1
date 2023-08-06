from setuptools import setup, find_packages

version = '0.4'

setup(name='on.sales',
      version=version,
      description="present a sales organisation to users",
      long_description="""\
Maintain a list of sales representatives and serviced areas along
with a mapping that allows users to quickly contact the relevant
sales personell.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      package_data = {
        '': ['*.txt', '*.rst', '*.py', '*.css', '*.xml', '*.zcml',
             '*.gif', '*.jpg', '*.png', '*.pot', '*.po'],
      },
      keywords='',
      author='Oeko.neT Mueller & Brandt GbR',
      author_email='support@oeko.net',
      url='http://www.oeko.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['on'],
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
