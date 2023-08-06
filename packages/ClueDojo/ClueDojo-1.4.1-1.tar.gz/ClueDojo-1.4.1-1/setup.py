from setuptools import setup, find_packages

version = '1.4.1-1'

setup(name='ClueDojo',
      version=version,
      description='Simple wsgi app to serve up Dojo',
      long_description='',
      classifiers=[],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://dev.serverzen.com/svn/cluemapper/ClueDojo/',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Paste',
          ],
      entry_points={
          'paste.app_factory': [
              'main=cluedojo.wsgiapp.make_app',
              ],
          },
      )
