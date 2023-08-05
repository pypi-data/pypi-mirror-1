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

        self.options['squid_config_dir'] = os.path.join(self.options['prefix'],
                                                        'etc')

        self.options['squid_cache_dir'] = os.path.join(self.options['prefix'],
                                                       'cache')
        self.options['squid_log_dir'] = os.path.join(self.options['prefix'],
                                                     'log')
        self.options['apache_conf_dir'] = os.path.join(self.options['prefix'],
                                                     'apache')
        self.options['debug_redirector']= self.options.get('debug_redirector','0')
        self.options['debug_squid_acl']= self.options.get('debug_squid_acl','0')
        self.options['debug_squid_rewrite_rules']= \
            self.options.get('debug_squid_rewrite_rules','0')

        self._get_zope_conf()

    def install(self):
        """installer"""
        # XXX do the job here
        # returns installed files

        owner = self.options.get('squid_owner')
        group = self.options.get('squid_group')
        #extra = '--with-owner=%s --with-group=%s' % (owner, group)
        #self.options['extra_options'] = extra

        curdir = os.path.dirname(__file__)
        self.create_all_directory()
        self._make_squid_conf()
        self._make_iredirector_conf()
        self._make_squidacl_conf()
        self._make_squidrewritesrules_conf()
        self._make_apacheconf()
        self._setup_right()

        return self.options['prefix']

    def create_all_directory(self):
        """
        create all necessary directory for buildout
        """
        for dir in ('squid_config_dir',
                    'squid_cache_dir',
                    'squid_log_dir',
                    'apache_conf_dir'):
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
            os.system( 'chown -R %s:%s %s' % (self.options['squid_owner'],
                                              self.options['squid_group'],
                                              root_path))
            ## make sure that python script are executable
            os.system( 'chmod ug+x %s/*.py' % (self.options['squid_config_dir']))







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
        self.apache_server_alias = []
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
                self.apache_server_alias.append(g[0])
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

        ## only generated per host
        p_acl_accelerated_url = 'acl accelerated_urls urlpath_regex ^/%(proto)s/%(host)s/%(port)s/'
        p_cache_acl_accelerated_url = 'acl accelerated_urls urlpath_regex ^/%(zope_cache_key)s/%(proto)s/%(host)s/%(port)s/'

        l_acl_accelerated_urls = []
        p_rewrite_url = """
(r'http://%(squid_localisation)s/%(proto)s/%(host)s/%(port)s/(.*)',
r'http://%(zope_host)s:%(zope_port)s/VirtualHostBase/%(proto)s/%(host)s:%(port)s/%(zope_path)s/VirtualHostRoot/\\1', 'P,L'),"""
        p_cache_rewrite_url = """
(r'http://%(squid_localisation)s/%(zope_cache_key)s/%(proto)s/%(host)s/%(port)s/(.*)',
r'http://%(zope_host)s:%(zope_port)s/VirtualHostBase/%(proto)s/%(host)s:%(port)s/%(zope_path)s/VirtualHostRoot/%(zope_cache_key)s/\\1', 'P,L'),"""
        p_acl_zope_cache_key='acl zope_cache_keys urlpath_regex %(zope_cache_key)s'
        l_acl_zope_cache_keys = []

        l_rewrite_urls = []
        self.front = []
        if self.options['front_http'] == '1':
            self.front.append(('http', 80))
        if self.options['front_https'] == '1':
            self.front.append(('https', 443))

        for (proto, port) in self.front:
            ## flag to generate unique host_name
            has_generate= {}
            for zconf in self.zope_confs:
                conf = {'proto': proto,
                        'port': port,
                        'host': zconf['host_name'],
                        'squid_localisation' : \
                             self.options.get('squid_localisation',
                                          '127.0.0.1'),
                        'zope_host': zconf['zope_host'],
                        'zope_port': zconf['zope_port'],
                        'zope_path': zconf['zope_path'],
                        }

                if not has_generate.has_key(zconf['host_name']):
                    l_acl_accelerated_urls.append(p_acl_accelerated_url % conf)

                l_rewrite_urls.append(p_rewrite_url % conf)
                ## and now if we have cache_key we generate configuration
                for cache_key in self.cache_key:
                    conf['zope_cache_key']=cache_key
                    l_rewrite_urls.append(p_cache_rewrite_url % conf)
                    if not has_generate.has_key(zconf['host_name']):
                        l_acl_accelerated_urls.append(p_cache_acl_accelerated_url % conf)
                has_generate[zconf['host_name']] = 1

        for cache_key in self.cache_key:
            l_acl_zope_cache_keys.append(p_acl_zope_cache_key % \
                                          {'zope_cache_key' : cache_key} )

        if len(l_acl_zope_cache_keys)>0:
            l_acl_zope_cache_keys.append('no_cache allow acl_zope_cache_keys')
            self.options['acl_zope_cache_keys'] =  os.linesep.join(l_acl_zope_cache_keys)

        else:
            self.options['acl_zope_cache_keys'] = ''

        self.options['squid_rewrite_rules'] = os.linesep.join(l_rewrite_urls)
        self.options['acl_accelerated_urls'] = os.linesep.join(l_acl_accelerated_urls)
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
        self._write_conf('squid.conf', conf)



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



    def _do_conf(self,select_tpl):
        """
        write iredirector conf
        """
        curdir = os.path.dirname(__file__)
        # select_tpl is the name of the template
        # like iRedirector.py_tmpl
        main_tp = open(os.path.join(curdir,'templates',select_tpl)).read()
        conf = main_tp % self.options
        file_name = self.options['squid_config_dir']
        self._write_conf(select_tpl[:-5], conf)

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
        self._do_conf('iRedirector.py_tmpl')


    def _make_squidacl_conf(self):
        """
        write squidacl conf
        """
        self._do_conf('squidAcl.py_tmpl')

    def _make_squidrewritesrules_conf(self):
        """
        write a squidrewritesrules conf
        """
        self._do_conf('squidRewriteRules.py_tmpl')





    def _make_apacheconf(self):
        """
        make apache conf for squid configuration
        """

        vhost_conf={'vhost_apache_zopeconf':'',
                    'vhost_apache_conf':''}

        for (proto, port) in self.front:
            conf = {'proto': proto,
                    'port': port,
                    'squid_localisation' : \

                        self.options.get('squid_localisation','127.0.0.1'),
                    'squid_port' : self.options['squid_port']
                    }



            ## generate specific configuration
            if self.cache_key:
                for zope_cache_key in self.cache_key:

                    conf['zope_cache_key'] = zope_cache_key
                    r = self._generate_template('vhost_zcache_tmpl',conf)
                    vhost_conf['vhost_apache_zopeconf']+=r
            ## generate configuration
            r = self._generate_template('vhost_common_tmpl',conf)
            vhost_conf['vhost_apache_conf'] = r
            vhost_conf['squid_visible_hostname'] = \
                self.options['squid_visible_hostname']
            vhost_conf['apache_server_alias'] = \
                ' '.join(self.apache_server_alias)
            vhost_conf['port'] = port
            vhost_conf['squid_log_dir'] = self.options['squid_log_dir']
            r = self._generate_template('vhost_squid.conf_tmpl',vhost_conf)
            ## and write specific conf for apache in conf/apache directory

            name_conf = 'vhost_%(squid_visible_hostname)s_%(port)s.conf' % vhost_conf
            name_apache_conf = os.path.join(self.options['apache_conf_dir'],
                                            name_conf)
            f = open(name_apache_conf,'w')
            f.write(r)



            ## and now write config
    def update(self):
        """updater"""
        pass

