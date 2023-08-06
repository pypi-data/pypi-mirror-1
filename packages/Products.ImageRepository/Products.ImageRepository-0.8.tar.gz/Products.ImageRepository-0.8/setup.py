from setuptools import setup, find_packages
from os.path import join

version = open(join('Products', 'ImageRepository', 'version.txt')).read().strip()
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'Products.ImageRepository',
      version = version,
      description = 'A centralized image repository with keyword/tag-based browsing and filtering.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'plone images repository centralized keywords',
      author = 'Jarn AS',
      author_email = 'info@jarn.com',
      url = 'http://pypi.python.org/pypi/Products.ImageRepository/',
      download_url = 'http://pypi.python.org/pypi/Products.ImageRepository/',
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['Products'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = ['setuptools',],
      entry_points = '',
)

