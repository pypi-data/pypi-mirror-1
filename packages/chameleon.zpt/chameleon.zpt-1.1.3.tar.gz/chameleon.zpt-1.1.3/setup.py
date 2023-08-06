from setuptools import setup
from setuptools import find_packages

version = '1.1.3'

install_requires = [
    'setuptools',
    'Chameleon>=1.0.1',
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
      include_package_data=True,
      namespace_packages=['chameleon'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      zip_safe=False,
      install_requires=install_requires,
      extras_require = {'test': install_requires},
      )
