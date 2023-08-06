from setuptools import setup, find_packages
from os.path import join

version = '1.0b1'
readme = open("README.txt").read()
history = open('HISTORY.txt').read()

setup(name='ely.croppableimagefield',
      version=version,
      description="CroppableImageField is a drop-in replacement for the Archetype field ImageField",
      long_description = readme + '\n' + history,
      classifiers=[
          "Framework :: Plone",
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ],
      author = 'Michael Dunstan',
      author_email = 'michael@elyt.com',
      url = 'http://pypi.python.org/pypi/ely.croppableimagefield',
      license = 'GPL',
      packages=find_packages(),
      namespace_packages=['ely'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      )
