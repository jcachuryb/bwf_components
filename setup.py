from setuptools import setup

setup(name='bwf_components',
      version='1.01',
      description='Business Workflow Components',
      url='https://github.com/dbca-wa/bwf_components',
      author='Department of Biodiversity, Conservation and Attractions',
      author_email='asi@dbca.wa.gov.au',
      license='BSD',
      packages=['ledger_api_client','ledger_api_client.migrations','ledger_api_client.management','ledger_api_client.management.commands',
                ],
      install_requires=['django-crispy-forms',],
      include_package_data=True,
      zip_safe=False)
