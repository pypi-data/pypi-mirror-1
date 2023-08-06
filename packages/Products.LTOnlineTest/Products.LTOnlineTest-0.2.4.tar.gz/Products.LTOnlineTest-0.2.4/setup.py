from setuptools import setup, find_packages

version = '0.2.4'

setup(name='Products.LTOnlineTest',
      version=version,
      description="An online Quiz product for CMF & Plone.",
      long_description=open("README.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone online quiz',
      author='Anton Hughes',
      author_email='antonh@lawtec.net',
      url='http://lawtec.net/projects/ltonlinetest',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
