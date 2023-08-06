
from setuptools import setup, find_packages 
setup(name='disthelper',
      version='0.9.2',
      description='helps you manage a Python distribution',
      long_description=open('./README.txt','r').read(),
      packages=find_packages(),
      author="Kumar McMillan",
      author_email="kumar.mcmillan@gmail.com",
      install_requires=['PasteScript'],
      tests_require=['nose', 'fixture', 'wikir'], # wikir for shelldoc, needs refactor
      url="http://code.google.com/p/disthelper/",
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