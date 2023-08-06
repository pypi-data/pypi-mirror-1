from setuptools import setup, find_packages

version = '0.1'

setup(name='Products.BooleanIndex',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Helge Tesdal',
      author_email='tesdal@jarn.com',
      url='http://pypi.python.org/pypi/Products.BooleanIndex',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
