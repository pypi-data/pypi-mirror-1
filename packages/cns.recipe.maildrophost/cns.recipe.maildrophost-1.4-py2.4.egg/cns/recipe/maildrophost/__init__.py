#
# This recipe is based on plone.recipe.distros and dist_plone.py script
# 

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import zc.buildout

class Recipe:
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        download_dir = self.buildout['buildout'].get('download-directory', \
            self.buildout['buildout'].get('download-cache', \
            os.path.join(self.buildout['buildout']['directory'],"downloads")))

        
        version = self.options.get('version')
        if version is None:
            version = '1.21'
        else:
            version = version.strip()
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            self.options.created(download_dir)
        target = self.options.get('target')
        if target is None:
            target = os.path.join(self.buildout['buildout']['directory'], 'products')
        result = None

        url = 'http://www.dataflake.org/software/maildrophost/maildrophost_%(version)s/MaildropHost-%(version)s.tgz' % {'version':version}
        fname = os.path.join(download_dir, url.split('/')[-1])
        # Have we already downloaded the file?
        if not os.path.exists(fname):
            f = open(fname, 'wb')
            try:
                f.write(urllib2.urlopen(url).read())
                f.close()
            except IOError, msg:
                raise
                
        setuptools.archive_util.unpack_archive(fname, target)
        result = os.path.join(target, 'MaildropHost')
        
        # configure config.py
        # Format of options is 
        #     key : type
        # Type may be string or number
        # string values are wrapped into quotes
        options = {'MAILDROP_HOME':'string',
                   'MAILDROP_SPOOL':'string',
                   'MAILDROP_VAR':'string',
                   'MAILDROP_PID_FILE':'string',
                   'MAILDROP_LOG_FILE':'string',
                   'PYTHON':'string',
                   'SMTP_HOST':'string',
                   'SMTP_PORT':'number',
                   'MAILDROP_INTERVAL':'number',
                   'DEBUG':'number',
                   'DEBUG_RECEIVER':'string',
                   'MAILDROP_BATCH':'number',
                   'MAILDROP_TLS':'number',
                   'MAILDROP_LOGIN':'string',
                   'MAILDROP_PASSWORD':'string',
                   'WAIT_INTERVAL':'number',
                   'ADD_MESSAGEID':'number',
                   'SUPERVISED_DAEMON':'number',
                   'MAILDROP_USER':'string',
                  }
        
        # prepare list of values
        values = {}
        for k, t in options.items():
            v = self.options.get(k)
            if v is not None:
                if t=='string':
                    values[k] = '"%s"' % v
                elif t=='number':
                    values[k] = v
                else:
                    raise Exception, 'Unknown variable type'
        
        # read old configuration
        config = open(os.path.join(result, 'config.py'), 'rU')
        old_config = config.readlines()
        config.close()
        
        # write new configuration
        config = open(os.path.join(result, 'config.py'), 'w')
        for line in old_config:
            processed = False
            for k,v in values.items():
                if line.startswith(k):
                    # replace old value with new one
                    config.write('%s=%s\n' % (k,v))
                    processed = True
                    break
            if not processed:
                config.write(line)
        config.close()
        
        # write control script to ${buildout:directory}/bin
        buildout_dir = self.buildout['buildout']['directory']
        # read maildropctl file
        fp = open(os.path.join(target, 'MaildropHost', 'maildrop', 'bin', 'maildropctl'), 'rU')
        old_ctl = fp.readlines()
        fp.close()
        
        # write new (configured) control file
        new_ctl_filename = os.path.join(buildout_dir, 'bin', 'maildropctl')
        new_ctl = open(new_ctl_filename, 'w')
        for line in old_ctl:
            processed = False
            if line.startswith('MAILDROP_DIR'):
                new_ctl.write('MAILDROP_DIR="%s"\n' % os.path.join(result, 'maildrop'))
                processed = True
            if line.startswith('MAILDROP_CONFIG_FILE'):
                new_ctl.write('MAILDROP_CONFIG_FILE="%s"\n' % os.path.join(result, 'config.py'))
                processed = True
            if line.startswith('MAILDROP_USER'):
                # maildrop user will be read from options or will be the same as current user
                v = self.options.get('MAILDROP_USER')
                if v is not None:
                    new_ctl.write('MAILDROP_USER="%s"\n' % v)
                else:
                    new_ctl.write('MAILDROP_USER=`id -un`\n')
                processed = True
            if not processed:
                new_ctl.write(line)
        new_ctl.close()
        os.chmod(new_ctl_filename, 0755)
        print "Wrote %s" % new_ctl_filename
        return result

    def update(self):
        pass
        
