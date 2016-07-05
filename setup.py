from setuptools import setup

setup(name='pasta',
     version='0.2',
      description='The Yangcong Data Requirement ToolKit',
      url='http://github.com/guanghetv/pasta',
      author='ronfe',
      author_email='hongfei@guanghe.tv',
      license='MIT',
      packages=['pasta'],
      install_requires=[
          'pymongo'
      ],
      scripts=["bin/pasta"],
      zip_safe=False)
