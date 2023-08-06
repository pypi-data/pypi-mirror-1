from setuptools import setup

version = '1.0'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f]
    f.close()
    return '\n'.join(s)

setup(name='ZenCheck',
      version=version,
      description='A wrapper for various code/markup syntax checking tools.',
      long_description=file_content('README.txt'),
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://dev.serverzen.com/svn/public/projects/ZenCheck/',
      license='BSD',
      py_modules=['zencheck'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'pep8 >= 0.3',
          'pyflakes >= 0.3',
          ],
      test_suite="zencheck.test_suite",
      entry_points={
          'console_scripts': [
              'zencheck = zencheck:main',
              ]},
      )
