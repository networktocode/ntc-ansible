import pathlib
from setuptools import setup, find_packages


CWD = pathlib.Path(__file__).parent
README = (CWD / "README.md").read_text()

setup(
  name='ntc-ansible',
  packages=find_packages(),
  version='0.9.1',
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
