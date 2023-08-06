from setuptools import setup

setup(name='TracSubPages',
      version='0.2',
      packages=['TracSubPages'],
      package_data={},
      author='Jimmy Theis',
      author_email='jet.he.is@gmail.com',
      description='A Trac macro that displays the bodies of wiki pages inside other wiki pages',
      long_description=open('README.txt').read(),
      url='http://www.sixfeetup.com',
      license='BSD',
      entry_points={'trac.plugins': ['TracSubPages = TracSubPages']},
)
