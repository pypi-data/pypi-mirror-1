from setuptools import setup, find_packages

version = '0.1'

setup(name='zptlint',
      version=version,
      description="Utility to debug Zope Page Templates",
      long_description=file('README.txt').read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
      ],
      keywords='zope',
      author='Balazs Ree',
      author_email='ree@ree.hu',
      url='http://trac.gotcha.python-hosting.com/file/bubblenet/pythoncode/'
          'zptlint/README.txt?format=txt',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'zope.pagetemplate',
      ],
      entry_points = {
        'console_scripts': [
            'zptlint = zptlint:run',
            ],
        },
      )
