import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name=u"canalweb",
      version="0.5",
      author="Frederic Gobry",
      author_email="gobry@yorglu.net",
      license="GPLv3",
      description="Offline viewing of Canal+ shows",
      url="http://github.com/chbug/canalweb",
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'canalweb = canalweb.cli:main',
            ],
        },
      )
