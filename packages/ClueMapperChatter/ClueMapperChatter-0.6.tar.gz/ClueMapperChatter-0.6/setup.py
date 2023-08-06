from setuptools import setup

version = '0.6'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f if x.strip() != ';-*-rst-*-']
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueMapperChatter',
      version=version,
      description="Instant messaging plugin for ClueMapper.",
      long_description=readme + "\n" + history,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='irc im',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://www.cluemapper.org',
      license='BSD',
      packages=['clue', 'clue.chatter'],
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'supybot >= 0.83, <= 0.83.9999',
      ],
      entry_points={
        'console_scripts': [
            'cluechatter-notify = clue.chatter.svnnotify:main',
            ]},
      )
