
from setuptools import setup, find_packages 
setup(name='disthelper',
      version='0.9',
      description='helps you manage a Python distribution',
      long_description='',
      packages=find_packages(),
      install_requires=['PasteScript'],
      tests_require=['nose', 'fixture'],
      license='New BSD License',
      entry_points="""
        [paste.global_paster_command]
        distcmd = disthelper.cmd:DistCmd
        
        [disthelper.distcmd_templates]
        distcmd = disthelper.templates:DistCmdPackage
        """,
      package_data={
        'disthelper': [
            'templates/distcmd_package/+package+/*.py',
            'templates/distcmd_package/+package+/distcmds/*.py',],
        },
      )