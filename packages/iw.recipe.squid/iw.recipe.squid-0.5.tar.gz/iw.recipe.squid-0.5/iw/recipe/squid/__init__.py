# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe squid"""

import os
import sys
import re
from fpformat import fix

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        self.options['location'] = location
        self.options['prefix'] = os.path.join(location, name)
        self.options['binary_location'] =  os.path.join(\
                                        buildout['buildout']['directory'],
                                        'bin')

        self.options['squid_config_dir'] = self.options.get('squid_config_dir',
                                                            os.path.join(self.options['prefix'],
                                                            'etc'))
        self.options['squid_config_file'] = os.path.join(self.options['squid_config_dir'],
                                                        'squid.conf')

        self.options['squid_cache_dir'] = self.options.get('squid_cache_dir',
                                                           os.path.join(self.options['prefix'],
                                                           'cache'))
        self.options['squid_log_dir'] = self.options.get('squid_log_dir',
                                                         os.path.join(self.options['prefix'],
                                                         'log'))
        self.options['squid_var_dir'] = self.options.get('squid_var_dir',
                                                        os.path.join(self.options['prefix'],
                                                         'var'))
        self.options['apache_conf_dir'] = self.options.get('apache_conf_dir',
                                                        os.path.join(self.options['prefix'],
                                                         'apache'))

        self.options['debug_redirector']= self.options.get('debug_redirector','0')
        self.options['debug_squid_acl']= self.options.get('debug_squid_acl','0')
        self.options['debug_squid_rewrite_rules']= \
            self.options.get('debug_squid_rewrite_rules','0')
        self.options['squid_executable']= self.options.get('squid_executable',
                                                           '/usr/sbin/squid')
        self._get_zope_conf()

    def install(self):
        """installer"""
        # XXX do the job here
        # returns installed files
        install_files = []
        owner = self.options.get('squid_owner')
        group = self.options.get('squid_group')
        #extra = '--with-owner=%s --with-group=%s' % (owner, group)
        #self.options['extra_options'] = extra

        curdir = os.path.dirname(__file__)
        self.create_all_directory()
        install_files.append(self._make_squid_conf())
        install_files.append(self._make_iredirector_conf())
        install_files.append(self._make_squidacl_conf())
        install_files.append(self._make_squidrewritesrules_conf())
        install_files += self._make_apacheconf()
        install_files.append(self._make_squidctl())
        install_files.append(self._make_logrotate())
        self._setup_right()
        return install_files
        #return [ os.path.join(self.options['prefix'], dir) for dir in dirs if \
        #        dir != 'cache' and dir != 'log']

    def create_all_directory(self):
        """
        create all necessary directory for buildout
        """
        for dir in ('squid_config_dir',
                    'squid_cache_dir',
                    'squid_log_dir',
                    'squid_var_dir',
                    'apache_conf_dir',
                    'binary_location'):
            try:
                os.makedirs(self.options[dir])


            except OSError,e:
                ## file exists
                if e.errno == 17:
                    pass

            except WindowsError,e:
                ## file exists
                pass
            except Exception,e:
                ## other raise
                raise e

    def _setup_right(self):
        """
        the python script must be executable
        and directory scructure must be owned by squid user
        """
        root_path = self.options['prefix']
        if os.sys.platform != "win32":
            ## make sure that root_path is owned by squid
            #os.system( 'chown -R %s:%s %s' % (self.options['squid_owner'],
            #                                  self.options['squid_group'],
            #                                  root_path))
            ## make sure that python script are executable
            os.system( 'chmod ug+x %s/*.py' % (self.options['squid_config_dir']))
            ## make sure that squid ctl is executable
            os.system( 'chmod ug+x %s/squidctl' % (self.options['binary_location']))







    def _get_zope_conf(self):
        """
        compute zope conf
        assume that zope conf is like that

           www.mysite.com: 127.0.0.1:8080/mysite
           mysite.com: 127.0.0.1:8080/mysite
           www.mysecondsite.com: 127.0.0.2:9080/mysite2
           mysecondsite.com: 127.0.0.2:9080/mysite2
        """
        self.zope_confs = []

        for zope_conf in self.options.get('squid_accelerated_hosts','').split(os.linesep):

            zope_conf = zope_conf.strip()
            p = re.compile("(.*): (.*):([0-9]+)/(.*)")
            m = re.match(p,zope_conf)

            if m:
                self.zope_confs.append({})
                g = m.groups()
                self.zope_confs[-1]['host_name'] = g[0]
                self.zope_confs[-1]['zope_host'] = g[1]
                self.zope_confs[-1]['zope_port'] = g[2]
                self.zope_confs[-1]['zope_path'] = g[3]

        if len(self.zope_confs) == 0:
            ## its not normal, this params mi
            raise AssertionError('squid_accelerated_hosts must be like www.mysite.com: 127.0.0.1:8080/mysite')
        self.cache_key=[]
        for cache_key in self.options.get('zope_cache_key','').split(os.linesep):
            zope_cache_key = cache_key.strip()
            if zope_cache_key:
                self.cache_key.append(zope_cache_key)


        ## now compute acl_zope_hosts  used in squid.conf in acl zope_servers

        zhosts = [ (zconf['zope_host'],1) for zconf in self.zope_confs ]
        ## get unique value
        zhosts = dict(zhosts).keys()

        ## define squid_visible_hostname if not define
        ## by default is the first host_name in zope_conf
        if not self.options.has_key('squid_visible_hostname'):
            self.options['squid_visible_hostname'] = self.zope_confs[0]['host_name']
        ## define default squid port
        if not self.options.has_key('squid_port'):
            self.options['squid_port'] = '3128'
        ## define default versionof squid
        if not self.options.has_key('squid_version'):
            self.options['squid_version'] = '2.6'
        ## make sure that squid version is a flaot
        self.options['squid_version'] = fix(float(self.options['squid_version']),
                                        1)
        if not self.options.has_key('squid_localisation'):
            self.options['squid_localisation'] = '127.0.0.1'

        if not self.options.has_key('squid_admin_email'):
            self.options['squid_admin_email'] = 'webmaster@%s' % (\
                                self.zope_confs[0]['host_name'])

        if not self.options.has_key('squid_cache_size_mb'):
            self.options['squid_cache_size_mb'] = '1000'

        if not self.options.has_key('front_https'):
            self.options['front_https'] = '0'
        if not self.options.has_key('front_http'):
            self.options['front_http'] = '1'
        if not self.options.has_key('squid_owner'):
            self.options['squid_owner'] = os.getlogin()
        if not self.options.has_key('squid_group'):
            self.options['squid_group'] = self.options['squid_owner']


        self.options['acl_zope_hosts'] = ' '.join(zhosts)


        l_rewrite_urls = []
        self.front = []

        if self.options['front_http'] == '1':
            bind_port = self.options.get('bind_apache_http', 80)
            self.front.append(('http', bind_port))

        if self.options['front_https'] == '1':
            bind_port_https = self.options.get('bind_apache_http', 443)
            self.front.append(('https',  bind_port))

        self.options['executable'] = sys.executable
        self.options['iredirector_thread'] = '0'
        if float(self.options['squid_version']) >= 2.6:
            self.options['iredirector_thread'] = '1'



        ## compute acl_accelerated_urls
        ## pattern like ^/http/10.37.129.2/80





    def _make_squid_conf(self):
        """
        genrate squid.conf
        """


        version = self.options['squid_version'].replace('.', '_')





        select_tpl = 'squid_cache_%s_%s.conf_tmpl' % (version,
                                                      os.sys.platform != "win32" and 'unix' or 'win')

        curdir = os.path.dirname(__file__)
        main_tp = open(os.path.join(curdir,'templates', 'squid' ,
                                   select_tpl)).read()
        ## make conf

        conf = main_tp % self.options

        ## write conf
        filename = self._write_conf('squid.conf', conf)
        return filename




    def _write_conf(self, filename, data):
        """
        helper method to write a file config in squid/etc
        """

        if not os.path.exists(self.options['prefix']):
            os.mkdir(self.options['prefix'])

        etc_dir = self.options['squid_config_dir']
        if not os.path.exists(etc_dir):
            os.mkdir(etc_dir)
        filename = os.path.join(etc_dir, filename)
        f = open(filename, 'w')
        try:
            f.write(data)
        finally:
            f.close()
        return filename



    def _do_conf(self,select_tpl):
        """
        write a template un squid_config_dir
        """
        curdir = os.path.dirname(__file__)
        # select_tpl is the name of the template
        # like iRedirector.py_tmpl
        main_tp = open(os.path.join(curdir,'templates',select_tpl)).read()
        conf = main_tp % self.options
        file_name = self.options['squid_config_dir']
        return self._write_conf(select_tpl[:-5], conf)

    def _generate_template(self,select_tpl,conf):
        """
        get the template and return result
        """
        curdir = os.path.dirname(__file__)
        main_tp = open(os.path.join(curdir,'templates',select_tpl)).read()

        return main_tp % conf



    def _make_iredirector_conf(self):
        """
        write iredirector conf
        """
        return self._do_conf('iRedirector.py_tmpl')


    def _make_squidacl_conf(self):
        """
        write squidacl conf
        """
        return self._do_conf('squidAcl.py_tmpl')

    def _make_squidrewritesrules_conf(self):
        """
        write a squidrewritesrules conf
        """
        return self._do_conf('squidRewriteRules.py_tmpl')





    def _make_apacheconf(self):
        """
        make apache conf for squid configuration
        """

        vhost_conf={'vhost_apache_zopeconf':'',
                    'vhost_apache_conf':''}
        install_files = []

        for (proto, port) in self.front:
            first = True
            for zconf in self.zope_confs:
                vhost_conf['vhost_apache_zopeconf']=''
                conf = {'proto': proto,
                        'port': port,
                        'squid_localisation' : \

                            self.options.get('squid_localisation','127.0.0.1'),
                        'squid_port' : self.options['squid_port'],
                        }
                conf.update(zconf)




                ## generate specific configuration
                if self.cache_key:
                    for zope_cache_key in self.cache_key:

                        conf['zope_cache_key'] = zope_cache_key
                        r = self._generate_template('vhost_zcache_tmpl',conf)
                        vhost_conf['vhost_apache_zopeconf']+=r
                ## generate configuration
                r = self._generate_template('vhost_common_tmpl',conf)
                vhost_conf['vhost_apache_conf'] = r
                vhost_conf['visible_hostname'] = \
                    conf['host_name']
                vhost_conf['port'] = port
                vhost_conf['squid_log_dir'] = self.options['squid_log_dir']
                vhost_conf['squid_localisation'] = self.options.get('squid_localisation','127.0.0.1')
                vhost_conf['squid_port'] =  self.options.get('squid_port')

                r = self._generate_template('vhost_squid.conf_tmpl',vhost_conf)
                ## and write specific conf for apache in conf/apache directory
                if first:

                    if vhost_conf['port'] != 80 and vhost_conf['port'] != 443:
                        ## add listen part if port is not in listen
                        r = "Listen %(port)s\nNameVirtualHost *:%(port)s\n" % vhost_conf + r
                    else:
                        r = "NameVirtualHost *:%(port)s\n" % vhost_conf + r
                    first = False
                name_conf = 'vhost_%(host_name)s_%(port)s.conf' % conf
                name_apache_conf = os.path.join(self.options['apache_conf_dir'],
                                                name_conf)
                install_files.append(name_apache_conf)
                f = open(name_apache_conf,'w')
                f.write(r)
                f.close()
        return install_files

    def _make_squidctl(self):
        """ make squid controler shell script """
        r = self._generate_template('squid/squidctl_tmpl',self.options)
        filename = os.path.join(self.options['binary_location'],'squidctl')
        f = open(filename,'w')
        f.write(r)
        f.close()
        return filename

    def _make_logrotate(self):
        """ do conf for log rotation for squid """
        r = self._generate_template('squid/squid_logrotate.conf_tmpl',self.options)
        filename = os.path.join(self.options['squid_config_dir'],'squid_logrotate.conf')
        f = open(filename,'w')
        f.write(r)
        f.close()
        return filename

            ## and now write config
    def update(self):
        """updater"""
        pass

