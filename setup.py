import os
from setuptools import setup, find_packages


CWD = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(CWD, "README.md")) as readme:
    README = readme.read()

setup(
  name='ntc-ansible',
  packages=find_packages(),
  version='0.9.2',
  description='Dependencies for NTC Ansible modules',
  long_description=README,
  long_description_content_type="text/markdown",
  author='Jason Edelman',
  author_email='jedelman8@gmail.com',
  url='https://github.com/networktocode/ntc-ansible',
  download_url='https://github.com/networktocode/ntc-ansible/tarball/0.1.0',
  install_requires=[
      'pynxos',
      'pyntc',
      'netmiko'
  ],
)
