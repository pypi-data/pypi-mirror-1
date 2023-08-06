from setuptools import setup, find_packages

version = '1.1.1'

install_requires = [
    'setuptools',
    'zope.interface',
    'zope.component',
    'zope.i18n >= 3.5',
    'zope.dottedname',
    'chameleon.core >= 1.0.2',
    ]

setup(name='chameleon.zpt',
      version=version,
      description="Zope Page Template engine based on Chameleon",
      long_description=open("README.txt").read() + '\n' +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Malthe Borch and the Zope Community',
      author_email='zope-dev@zope.org',
      url='',
      license='BSD',
      namespace_packages=['chameleon'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require = {'test': install_requires},
      )
