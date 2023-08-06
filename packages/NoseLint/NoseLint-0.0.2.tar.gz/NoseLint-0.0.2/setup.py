from setuptools import setup

setup(name='NoseLint',
      version='0.0.2',
      entry_points = { 'nose.plugins.0.10':
                       ['pylint = noselint.pylintplugin:PyLintPlugin']
                       },
      author='James Casbon',
      author_email='casbon@gmail.com',
      packages=['noselint'],
      )
