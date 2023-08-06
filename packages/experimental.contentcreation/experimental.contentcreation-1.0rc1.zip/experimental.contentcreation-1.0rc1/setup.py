from setuptools import setup, find_packages

version = '1.0rc1'

setup(name='experimental.contentcreation',
      version=version,
      description="Experimental performance improvements to content creation",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Plone Community',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/experimental.contentcreation',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
