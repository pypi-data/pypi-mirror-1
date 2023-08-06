from setuptools import setup, find_packages
from os.path import join

version = '1.0a1'
readme = open(join('mr', 'bent', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'mr.bent',
      version = version,
      description = 'Mr. Bent knows his numbers.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'statistics profiling',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://dev.plone.org/collective/browser/mr.bent',
      download_url = 'http://cheeseshop.python.org/pypi/mr.bent/',
      license = 'BSD',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['mr'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = [
          'setuptools',
      ],
      tests_require = [
          'zope.testing',
      ],
      entry_points = '',
)
