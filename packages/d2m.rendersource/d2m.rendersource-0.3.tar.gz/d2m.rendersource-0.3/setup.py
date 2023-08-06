from setuptools import setup, find_packages

version = '0.3'

setup(name='d2m.rendersource',
      version=version,
      description="Grok source renderers",
      long_description="""\
""",
      classifiers=[], 
      keywords="",
      author="d2m",
      author_email="michael@d2m.at",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      namespace_packages=['d2m'],      
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        # -*- Extra requirements: -*-
                        ],
      entry_points = """
      """,
       )
