from setuptools import setup, find_packages

version = '0.6.2'

setup(name='externalator',
      version=version,
      description="svn bundle manager",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='The Open Planning Project',
      author_email='jhammel@openplans.org,info@openplans.org',
      url='http://openplans.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        # -*- Extra requirements: -*-
        'topp.utils',
      ],
      entry_points="""
      [console_scripts]
      externalator = externalator:main
      """,
      dependency_links=["https://svn.openplans.org/svn/topp.utils#egg=topp.utils-dev"],
      )
