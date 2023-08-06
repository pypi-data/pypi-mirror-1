from setuptools import setup, find_packages

version = '0.1b1'

setup(name='garbas.watermark',
      version=version,
      description="AT Image field with watermark",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone',
      author='Rok Garbas',
      author_email='rok.garbas@gmail.com',
      url='http://github.com/garbas/garbas.watermark',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['garbas'],
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
