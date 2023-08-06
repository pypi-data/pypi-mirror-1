from setuptools import setup

setup(name='TracSubPages',
      version='0.1',
      packages=['TracSubPages'],
      package_data={},
      author='Jimmy Theis',
      author_email='jet.he.is@gmail.com',
      description='Create wiki pages that are collections of smaller pages in Trac',
      long_description=open('README.txt').read(),
      url='http://www.sixfeetup.com',
      license='BSD',
      entry_points={'trac.plugins': ['TracSubPages = TracSubPages']},
)
