from setuptools import setup, find_packages

version = '0.4.2'

setup(name='experimental.portalfactoryfix',
      version=version,
      description="Plone fix for portal factory not to cause zodb writes",
      long_description=open("README.txt").read() + '\n\n' + open('CHANGES.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      url='http://dev.plone.org/collective/browser/experimental.portalfactoryfix',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
