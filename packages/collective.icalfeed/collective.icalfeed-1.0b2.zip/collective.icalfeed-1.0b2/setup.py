from setuptools import setup, find_packages
from os.path import join

version = '1.0b2'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'collective.icalfeed',
      version = version,
      description = 'View for rendering event content as an iCalendar feed.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        "Framework :: Plone",
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'plone events ical feed',
      author = 'Andreas Zeidler - Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://pypi.python.org/pypi/collective.icalfeed',
      license = 'GPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['collective'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = [
          'setuptools',
          'plone.memoize',
      ],
      entry_points = '',
)
