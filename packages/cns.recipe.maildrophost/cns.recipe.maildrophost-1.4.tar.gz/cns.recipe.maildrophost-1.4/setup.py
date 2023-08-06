from setuptools import setup, find_packages

version = '1.4'
name='cns.recipe.maildrophost'
setup(name=name,
      version=version,
      description="Recipe for installing MaildropHost",
      long_description="""\
cns.recipe.maildrophost is simple recipe used for installing MaildropHost from tarball with ability 
to configure the product by modifying config.py file. No other changes, except download, untar and modify
config.py are made.

Example::

  [maildrophost]
  recipe = cns.recipe.maildrophost
  version = 1.21
  target = ${buildout:directory}/products
  MAILDROP_HOME=/tmp/maildrop
  MAILDROP_SPOOL=/tmp/maildrop/spool
  MAILDROP_VAR=/tmp/maildrop/var
  MAILDROP_PID_FILE=/var/run/maildrop/maildrop.pid
  MAILDROP_LOG_FILE=/var/log/maildrop/maildrop.log
  PYTHON=/usr/bin/python
  SMTP_HOST=localhost
  SMTP_PORT=25
  MAILDROP_INTERVAL=120
  DEBUG=0
  DEBUG_RECEIVER=
  MAILDROP_BATCH=0
  MAILDROP_TLS=0
  MAILDROP_LOGIN=
  MAILDROP_PASSWORD=
  WAIT_INTERVAL=0.0
  ADD_MESSAGEID=0
  SUPERVISED_DAEMON=0


**version** is optional and defaults to 1.21

**target** is optional. Defaults to *${buildout:directory}/products* 

All other options (with capital letters) are MaildropHost specific options. See `MaildropHost/config.py <http://svn.dataflake.org/MaildropHost/trunk/config.py?content-type=text/plain>`_ 
for exact meaning.

Option **MAILDROP_USER** (not included above) is specific to maildropctl control script, 
which is generated to ${buildout:directory}/bin. If you want to run maildrop process under specific user, 
add MAILDROP_USER option to the buildout configuration. Otherwise current user will be used to start maildrop 
daemon process.

Do not change anything in MaildropHost directory by hand!

**Version 1.4**

Fixed MAILDROP_USER option. This option did not work. Thanks to dhigu.

**Version 1.3**

Fixed download_dir - if download_directory is not available using download_cache or downloads dir in buildout.

""",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='buildout recipe',
      author='Radim Novotny',
      author_email='radim.novotny@corenet.cz',
      url='http://svn.plone.org/svn/collective/cns.recipe.maildrophost',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cns', 'cns.recipe'],
      include_package_data=True,
      zip_safe=False,
	  install_requires = ['zc.buildout', 'setuptools'],
      entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
      )
