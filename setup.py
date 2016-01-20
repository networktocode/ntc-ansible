from setuptools import setup, find_packages

setup(
  name='ntc-ansible',
  packages=find_packages(),
  version='0.1.0',
  description='Dependencies for NTC Ansible modules',
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
