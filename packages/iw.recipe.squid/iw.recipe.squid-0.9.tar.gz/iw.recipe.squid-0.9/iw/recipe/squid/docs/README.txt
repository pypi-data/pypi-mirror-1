=======================
iw.recipe.squid package
=======================

.. contents::

What is iw.recipe.squid ?
=========================

Install squid proxy server and all specific python script in order to work with
an zope server or an zeo cluster

Do you have an example of build out ?
=====================================

Add into your `buildout.cfg` a section::

    [buildout]
    parts =
       ...
       squid

    [squid]
    recipe = iw.recipe.squid

    squid_accelerated_hosts =
        www.mysite.org: 127.0.0.1:8080/mysite

where options are:


- squid_accelerated_hosts : a list that configure your zope backend like this
  pattern::

    visible_host_name: <zope ip_or_host_name>:<zope list port>/<zope path>

optionnal options are:

- url : url to download squid src in order to compile it (todo)
- squid_owner : squid_owner of squid process (user login by default)
- location: location of squid install (by default parts-directory/squid of buildout)
- squid_visible_hostname: host name show in error messages (by default the first
  visible_host_name in squid_accelerated_host , www.mysite.org )
- squid_port : port of squid (3128 by default)
- squid_version : version of squid (2.6 by default)
- squid_localisation : where squid is for apache (127.0.0.1 by default, squid and
  apache are in the same host)
- squid_executable : location of squid binary executable (by default /usr/sbin/squid)
- squid_admin_email : email of the admin squid (by default webmaster@www.mysite.org)
- squid_cache_size_mb : size disk cache in mb (1000 by default)
- squid_config_dir : the config directory of squid ( parts-directory/squid/etc by default)
- squid_cache_dir : the cache localisation of squid (parts-directory/squid/cache by default)
- squid_log_dir : the log localisation of squid (parts-directory/squid/log by default)
- apache_conf_dir : the apache config dir (parts-directory/squid/apache by default)
- front_http : 1 by default (ie apache serve http request)
- front_https : 0 by default (ie apache serve https request)
- debug_redirector : 0 by default (ie debug squid redirector)
- debug_squid_acl : 0 by default (ie debug squid acl)
- debug_squid_rewrite_rules : 0 by default (ie debug squid acl)
- debug_apache_rewrite_rules : 0 by default (ie debug apache rewrite rules , 9 for full debug)
- zope_cache_key : a list of zope cache key (if you want to cache specific
  zone of your site add specific acl)
- bind_apache_http : binding ip\:port of apache (80 by default in http, can be only port configure)
- bind_apache_https : binding ip\:port of apache (443 by default in https, can be only port configure)


buildout command create a directory structure like that::

    parts/squid/apache/vhost_www.mysite.org_80.conf : virtual host to include to apache
    parts/squid/etc/ : all config file for squid
    parts/squid/etc/squid.conf : main squid conf
    parts/squid/etc/iRedirector.py : to launch squidRewriteRules
    parts/squid/etc/squidAcl.py : avoid cache authenticated user by squid
    parts/squid/etc/squidRewriteRules.py : rewrite engine for squid
    parts/squid/etc/squid_logrotate.conf : config for log rotate system (for logrotate system)
    parts/squid/cache/ : cache directory
    parts/squid/log/ : logs directory
    parts/squid/var/ : var directory, contains pid file
    bin/squidctl : squid controler shell script (for unix),
    Usage: squidctl {start|stop|reload|restart|status|debug|purgecache|createswap|configtest|rotate}



What about squid and apache after conf generation ?
===================================================

Apache
++++++

Activate virtual hosts by making a symbolic link

In debian::

    ln -s .../parts/squid/apache/vhost_www.mysite.org_80.conf /etc/apache2/sites-enabled/

Make sure that mod_rewrite, mod_proxy are enabled for apache

Logs are in parts/squid/log

Squid
+++++

To populate squid directory cache::

    /usr/sbin/squid -z -f parts/squid/etc/squid.conf OR
    bin/squidctl createswap

To launch squid the generated config::

    /usr/sbin/squid -f parts/squid/etc/squid.conf OR
    bin/squidctl start

That all's folk


How to use iw.recipe.squid ?
============================


As a recipe, you have to provide a part in your buildout file
Test first the most simple part that we can configure::


    >>> import getpass
    >>> owner = group = getpass.getuser()
    >>> import os
    >>> data_dir = os.path.join(test_dir, 'data')
    >>> parts_dir = os.path.join(data_dir, 'parts')
    >>> buildout = {'instance': {'location': test_dir},
    ...             'buildout': {'directory': test_dir,
    ...                          'parts-directory': test_dir}}
    >>> name = 'squid'
    >>> options = {'url': 'mypackage.tgz', #url where we download squid src
    ...            'squid_owner' : 'proxy',
    ...            }
    >>> options['squid_accelerated_hosts'] = """
    ...    www.mysite.com: 127.0.0.1:8080/mysite
    ... """

    Creating the recipe::

    >>> from iw.recipe.squid import Recipe
    >>> recipe = Recipe(buildout, name, options)

    Test that zope conf is good::

    >>> recipe.zope_confs
    [{'zope_host': '127.0.0.1', 'zope_path': 'mysite', 'host_name': 'www.mysite.com', 'zope_port': '8080'}]

    >>> recipe.options['squid_visible_hostname']
    'www.mysite.com'

    >>> recipe.options['front_https']
    '0'

    >>> recipe.options['squid_admin_email']
    'webmaster@www.mysite.com'

    >>> recipe.options['squid_version']
    '2.6'

    >>> recipe.options['binary_location']
    '.../bin'

    >>> paths = recipe.install()

Checking the files created::


    >>> paths.sort()
    >>> paths
    ['...squid/tests/bin/squidctl', '...squid/tests/squid/apache/vhost_www.mysite.com_80.conf', '...squid/tests/squid/etc/iRedirector.py', '...squid/tests/squid/etc/squid.conf', '...squid/tests/squid/etc/squidAcl.py', '...squid/tests/squid/etc/squidRewriteRules.py', '...squid/tests/squid/etc/squid_logrotate.conf']



The default generated squid.conf
++++++++++++++++++++++++++++++++

    >>> cfg = os.path.join(recipe.options['prefix'], 'etc', 'squid.conf')
    >>> print open(cfg).read()
    # squid configuration file
    <BLANKLINE>
    # BASIC CONFIGURATION
    # ------------------------------------------------------------------------------
    #  TAG: visible_hostname
    #    If you want to present a special hostname in error messages, etc,
    #    define this.  Otherwise, the return value of gethostname()
    #    will be used. If you have multiple caches in a cluster and
    #    get errors about IP-forwarding you must set them to have individual
    #    names with this setting.
    visible_hostname www.mysite.com
    <BLANKLINE>
    cache_effective_user proxy
    cache_effective_group proxy
    <BLANKLINE>
    # port on which to listen
    <BLANKLINE>
    http_port 3128 vhost defaultsite=www.mysite.com
    <BLANKLINE>
    <BLANKLINE>
    cache_dir ufs .../squid/cache 1000  16     256
    cache_mgr webmaster@www.mysite.com
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    # LOGS
    # ------------------------------------------------------------------------------
    log_icp_queries off
    cache_access_log .../squid/log/access.log
    cache_log .../squid/log/cache.log
    cache_store_log .../squid/log/store.log
    # emulate_httpd_log off
    <BLANKLINE>
    <BLANKLINE>
    # RESOURCES
    # ------------------------------------------------------------------------------
    # amount of memory used for caching recently accessed objects - defaults to 8 MB
    cache_mem 64 MB
    maximum_object_size 10 MB         # max cached object size
    maximum_object_size_in_memory 300 KB    # max cached-in-memory object size
    <BLANKLINE>
    <BLANKLINE>
    # ACCESS CONTROL
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    # Basic ACLs
    acl all src 0.0.0.0/0.0.0.0
    acl localhost src 127.0.0.1/32
    acl ssl_ports port 443 563
    acl safe_ports port 80 443
    <BLANKLINE>
    <BLANKLINE>
    acl zope_servers src 127.0.0.1
    #acl zope_servers src 127.0.0.1
    <BLANKLINE>
    acl manager proto cache_object
    acl connect method connect
    <BLANKLINE>
    # Assumes apache rewrite rule looks like this:
    # RewriteRule ^/(.*)/$ http://127.0.0.1:3128/http/%{SERVER_NAME}/80/$1 [L,P]
    <BLANKLINE>
    acl accelerated_protocols proto http
    acl accelerated_hosts dst 127.0.0.0/8
    acl accelerated_ports myport 3128
    acl accelerated_urls urlpath_regex __original_url__
    acl accelerated_urls urlpath_regex __zope_cache_key__.*__cache_url__
    <BLANKLINE>
    <BLANKLINE>
    http_access allow accelerated_hosts
    http_access allow accelerated_ports
    http_access allow accelerated_urls
    http_access allow accelerated_protocols
    <BLANKLINE>
    always_direct allow accelerated_hosts
    always_direct allow accelerated_ports
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    # Purge access - zope servers can purge but nobody else
    acl purge method PURGE
    http_access allow zope_servers purge
    http_access deny purge
    <BLANKLINE>
    # Reply access
    # http_reply_access allow all
    <BLANKLINE>
    # Cache manager setup - cache manager can only connect from localhost
    # only allow cache manager access from localhost
    http_access allow manager localhost
    http_access deny manager
    # deny connect to other than ssl ports
    http_access deny connect !ssl_ports
    <BLANKLINE>
    # ICP access - anybody can access icp methods
    icp_access allow localhost zope_servers
    <BLANKLINE>
    # And finally deny all other access to this proxy
    http_access deny all
    <BLANKLINE>
    <BLANKLINE>
    # CACHE PEERS
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    # CONFIGURE THE CACHE PEERS. FIRST PORT IS THE HTTP PORT, SECOND PORT
    # IS THE ICP PORT. REMEMBER TO ENABLE 'icp-server' ON YOUR 'zope.conf'
    # LISTENING ON THE ICP PORT YOU USE HERE.
    # acl in_backendpool dstdomain backendpool
    # cache_peer 127.0.0.1 parent 8080 9090 no-digest no-netdb-exchange
    # cache_peer 192.168.0.3 parent 8081 9091 no-digest no-netdb-exchange
    <BLANKLINE>
    # cache_peer_access 127.0.0.1 allow in_backendpool
    # cache_peer_access 127.0.0.1 deny all
    <BLANKLINE>
    # cache_peer_access 192.168.0.3 allow in_backendpool
    # cache_peer_access 192.168.0.3 deny all
    <BLANKLINE>
    # IF YOU NEED TO FORWARD REQUESTS TO HOSTS NOT IN THE POOL THIS IS
    # WHERE YOU ALLOW THE TARGET DOMAINS
    # acl local_servers dstdomain some.mysite.com other.mysite.com
    # always_direct allow local_servers
    <BLANKLINE>
    # THE FOLLOWING DIRECTIVE IS NEEDED TO MAKE 'backendpool' RESOLVE TO
    # THE POOL OF CACHE PEERS.
    # never_direct allow all
    # icp_access allow all
    <BLANKLINE>
    # PROXY ON, NEEDED TO MAKE CACHE PEERS INTERCOMMUNICATE
    # httpd_accel_with_proxy on
    <BLANKLINE>
    <BLANKLINE>
    # REDIRECTOR PROGRAM
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    <BLANKLINE>
    redirect_program .../squid/etc/iRedirector.py
    url_rewrite_children 1
    url_rewrite_concurrency 20
    url_rewrite_host_header off
    <BLANKLINE>
    <BLANKLINE>
    # SPECIFY WHAT REQUESTS SQUID SHOULD CACHE
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    # Control what squid caches.  We want to have squid handle content that is not
    # personalized and that does not require any kind of authorization.
    # 1) Always cache static content in squid
    <BLANKLINE>
    acl static_content urlpath_regex -i \.(jpg|jpeg|gif|png|tiff|tif|svg|swf|ico|css|js|vsd|doc|ppt|pps|xls|pdf|mp3|mp4|m4a|ogg|mov|avi|wmv|sxw|zip|gz|bz2|tgz|tar|rar|odc|odb|odf|odg|odi|odp|ods|odt|sxc|sxd|sxi|sxw|dmg|torrent|deb|msi|iso|rpm)$
    no_cache allow static_content
    <BLANKLINE>
    # 2) (OPTIONAL) Prevent squid from caching an item that is the result of a POST
    <BLANKLINE>
    acl post_requests method POST
    no_cache deny post_requests
    <BLANKLINE>
    # 3) (OPTIONAL) Prevent squid from caching items with items in the query string
    # If this is uncommented, squid will treat a url with 2 different query strings
    # as 2 different urls when caching.
    <BLANKLINE>
    # XXX: where did this example go?
    <BLANKLINE>
    <BLANKLINE>
    acl zope_key_caching urlpath_regex d41d8cd98f00b204e9800998ecf8427e
    no_cache allow zope_key_caching
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    # 4) Prevent squid from caching requests from authenticated users or conditional
    # GETs with an If-None-Match header (since squid doesn't know about ETags)
    # We use an external python method to check these conditions and pass in the
    # value of the __ac cookie (two different ways to allow for different cookie
    # delimiters), the HTTP Authorization header, and the If-None-Match header.
    # Squid caches the results of the external python method, so for debugging, set
    # the options ttl=0 negative_ttl=0 so you can see what is going on
    <BLANKLINE>
    # external_acl_type is_cacheable_type children=20 ttl=0 negative_ttl=0 %{Cookie:__ac} %{Cookie:;__ac} %{Authorization} %{If-None-Match} .../squid/etc/squidAcl.py
    <BLANKLINE>
    external_acl_type is_cacheable_type protocol=2.5 children=20 %{Cookie:__ac} %{Cookie:;__ac} %{Authorization} %{If-None-Match} .../squid/etc/squidAcl.py
    acl is_cacheable external is_cacheable_type
    no_cache allow is_cacheable
    <BLANKLINE>
    collapsed_forwarding on
    <BLANKLINE>
    # Explicitly disallow squid from handling anything else
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    no_cache deny all
    <BLANKLINE>
    <BLANKLINE>
    # SPECIFY EFFECTS OF A BROWSER REFRESH
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    # RELOAD_INTO_IMS CAUSES WEIRD SQUID BEHAVIOR - IT APPEARS TO CAUSE FILES WITH
    # INAPPROPRIATE HEADERS TO END UP IN THE CACHE, AND AS A RESULT BROWSERS END
    # UP MAKING LOTS OF EXTRA (CONDITIONAL) REQUESTS WHEN THEY WOULD OTHERWISE MAKE
    # NO REQUESTS.  DO NOT USE!
    <BLANKLINE>
    # Tell squid how to handle expiration times for content with no explicit expiration
    # Assume static content is fresh for at least an hour and at most a day
    #refresh_pattern -i  \.(jpg|jpeg|gif|png|tiff|tif|svg|swf|ico|css|js|vsd|doc|ppt|pps|xls|pdf|mp3|mp4|m4a|ogg|mov|avi|wmv|sxw|zip|gz|bz2|tar|rar|odc|odb|odf|odg|odi|odp|ods|odt|sxc|sxd|sxi|sxw|dmg|torrent|deb|msi|iso|rpm)$ 60 50% 1440 reload-into-ims
    #refresh_pattern . 0 20%    1440
    <BLANKLINE>
    # Change force-refresh requests into conditional gets using if-modified-since
    #reload_into_ims on
    <BLANKLINE>
    # DEBUGGING
    # ------------------------------------------------------------------------------
    # debug_options ALL,1 33,2 # use this for debugging acls
    # debug_options ALL,8
    <BLANKLINE>
    <BLANKLINE>
    # MISCELLANEOUS
    # ------------------------------------------------------------------------------
    # have squid handle all requests with ranges
    # range_offset_limit -1
    <BLANKLINE>
    # amount of time squid waits for existing requests to be serviced before shutting down
    shutdown_lifetime 1 seconds
    <BLANKLINE>
    # allow squid to process multiple requests simultaneously if client is pipelining
    pipeline_prefetch on
    <BLANKLINE>
    # allow white spaces to be included in URLs
    uri_whitespace allow
    <BLANKLINE>
    <BLANKLINE>
    # OTHER PARAMETERS THAT MAY BE OF INTEREST
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    # logfile_rotate 0
    # reload_into_ims off
    # error_directory /usr/share/squid/errors/
    <BLANKLINE>
    pid_filename .../squid/var/squid.pid
    <BLANKLINE>

The default generated squidRewriteRules.py
++++++++++++++++++++++++++++++++++++++++++


    >>> cfg = os.path.join(recipe.options['prefix'], 'etc', 'squidRewriteRules.py')
    >>> print open(cfg).read()
    #!...
    rewrites = (
    (r'http://127.0.0.1/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)/(.*)/__original_url__/(.*)',
    r'http://\1:\2/VirtualHostBase/\3/\4:\5/\6/VirtualHostRoot/\7', 'P,L'),
    (r'http://127.0.0.1/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)/(.*)/__zope_cache_key__/(.*)/__cache_url__/(.*)',
    r'http://\1:\2/VirtualHostBase/\3/\4:\5/\6/VirtualHostRoot/\7/\8', 'P,L'),
    <BLANKLINE>
        )
    ...

The default generated conf for apache
+++++++++++++++++++++++++++++++++++++

    >>> cfg = os.path.join(recipe.options['prefix'], 'etc', 'squidRewriteRules.py')
    >>> print open(cfg).read()
    #!...

    >>> cfg = os.path.join(recipe.options['prefix'], 'apache', 'vhost_www.mysite.com_80.conf')
    >>> print open(cfg).read()
    NameVirtualHost *:80
    <VirtualHost *:80>
        ServerName www.mysite.com
    <BLANKLINE>
        <Proxy http://127.0.0.1:3128>
                Allow from all
        </Proxy>
    <BLANKLINE>
    <BLANKLINE>
        RewriteEngine On
        RewriteLog .../squid/log/rewrite_www.mysite.com.log
        RewriteLogLevel 0
    <BLANKLINE>
        CustomLog .../squid/log/access_www.mysite.com.log common
        ErrorLog .../squid/log/error_www.mysite.com.log
    <BLANKLINE>
        RewriteRule ^(.*)$ - [E=BACKEND_LOCATION:127.0.0.1]
        RewriteRule ^(.*)$ - [E=BACKEND_PORT:8080]
        RewriteRule ^(.*)$ - [E=BACKEND_PATH:mysite]
    <BLANKLINE>
    <BLANKLINE>
        RewriteRule  ^/(.*)/$ http://127.0.0.1:3128/%{ENV:BACKEND_LOCATION}/%{ENV:BACKEND_PORT}/http/%{SERVER_NAME}/80/%{ENV:BACKEND_PATH}/__original_url__/$1 [L,P]
        RewriteRule  ^/(.*)$ http://127.0.0.1:3128/%{ENV:BACKEND_LOCATION}/%{ENV:BACKEND_PORT}/http/%{SERVER_NAME}/80/%{ENV:BACKEND_PATH}/__original_url__/$1 [L,P]
    <BLANKLINE>
    <BLANKLINE>
    </VirtualHost>
    <BLANKLINE>

/bin/squidacl file
++++++++++++++++++

    >>> f = open(os.path.join(recipe.options['binary_location'],'squidctl'))
    >>> print f.read()
    #!/bin/sh
    ...
    DAEMON=/usr/sbin/squid
    CONFIG=.../squid/etc/squid.conf
    CACHE_DIR=.../squid/cache
    ...

etc/squid_logrotate.conf
++++++++++++++++++++++++

    >>> cfg = os.path.join(recipe.options['prefix'], 'etc', 'squid_logrotate.conf')
    >>> print open(cfg).read()
    /.../squid/var/*.log {
        weekly
        compress
        delaycompress
        maxage 730
        rotate 104
        size=+4096k
        notifempty
        missingok
        create 740 proxy proxy
        postrotate
        .../bin/squidctl rotate
        endscript
    }



More options
++++++++++++

Give more options to the recipe::

    >>> options = {'url': 'mypackage.tgz', #url where we download squid src
    ...            'squid_owner': owner, #owner of squid process
    ...            'squid_group' : group, #group of squid process
    ...            'squid_port' : '3128', #listen port of proxy
    ...            'squid_version' : '2.5',
    ...            'squid_localisation': '127.0.0.1', #host or ip that apache use to request apache
    ...
    ...            'squid_admin_email' : 'myemail@mycompany.com', #name appear in error message
    ...            'squid_cache_size_mb' : '1000', #total cache in disk
    ...            'squid_visible_hostname' : 'mysite', #public name of your site, appear in error message
    ...            'front_https': '1', # does front server (apache, iis)
    ...                              # serve https url O by default
    ...            'front_http':'1', # does front server (apache, iis) serve http url
    ...            'bind_apache_http':'81', # change the default binding port of apache
    ...            'debug_redirector':'1', #debug iRedirector 0 by default
    ...            'debug_squid_acl' : '0', #debug squidacl 0 by default
    ...            'debug_squid_rewrite_rules' : '1', #debug squidtrewriterule 0 by default
    ...            'debug_apache_rewrite_rules' : '9', #debug apache rewrite engine
    ...           }


Yours accelerated hosts ( zeo client or pound load balancer ,
urls to be accelerated wich corresponding of zope urls, ports, and directories)::

    >>> options['squid_accelerated_hosts'] = """
    ...    www.mysite.com: 127.0.0.1:8080/mysite
    ...    mysite.com: 127.0.0.1:8080/mysite
    ...    www.mysecondsite.com: 127.0.0.2:9080/mysite2
    ...    mysecondsite.com: 127.0.0.2:9080/mysite2
    ... """

This parts is optionnal. We can cache in proxy some part of navigation via
specific configuration. This is sometimes usefull to cache zope pages per groups
or via specific cookies rules. This configuration is done by zope_cache_keys.
Be carefull : CMFSquid don't purge this url without an intervention of your part.
Assumes that zope_cache_keys are cookies that is send by zope
and you have created a folder in zodb name as your cache key to do job acquisition
Specific rewrites rules and squid are build::

    >>> options['zope_cache_key'] = """
    ...    my_key_one
    ...    my_key_two
    ...    my_key_three
    ... """


Creating the recipe::

    >>> from iw.recipe.squid import Recipe
    >>> recipe = Recipe(buildout, name, options)

Test that zope conf is good::

    >>> recipe.zope_confs
    [{'zope_host': '127.0.0.1', 'zope_path': 'mysite', 'host_name': 'www.mysite.com', 'zope_port': '8080'}, {'zope_host': '127.0.0.1', 'zope_path': 'mysite', 'host_name': 'mysite.com', 'zope_port': '8080'}, {'zope_host': '127.0.0.2', 'zope_path': 'mysite2', 'host_name': 'www.mysecondsite.com', 'zope_port': '9080'}, {'zope_host': '127.0.0.2', 'zope_path': 'mysite2', 'host_name': 'mysecondsite.com', 'zope_port': '9080'}]


Zope acl are ip or host that is configure in squid in order
to be host or ip authorized to purge cache squid.

Test zope acl::

    >>> recipe.options['acl_zope_hosts']
    '127.0.0.2 127.0.0.1'

Test rewrites rules::

    >>> recipe.cache_key
    ['my_key_one', 'my_key_two', 'my_key_three']



Running it::


    >>> paths = recipe.install()

Checking the files created::

    >>> path = recipe.options['prefix']

Checking the squid.conf created::

    >>> cfg = os.path.join(path, 'etc', 'squid.conf')
    >>> print open(cfg).read()
    # squid configuration file
    ...
    http_port 3128
    ...
    httpd_accel_host virtual
    httpd_accel_port 81
    httpd_accel_uses_host_header on
    ...
    redirect_children 20
    redirect_rewrites_host_header off
    ...

Checking if we have generate iRedirector conf::

    >>> cfg = os.path.join(path, 'etc', 'iRedirector.py')
    >>> print open(cfg).read()
    #!...
    threaded =  0...

    >>> cfg = os.path.join(path, 'etc', 'squidAcl.py')
    >>> print open(cfg).read()
    #!...

Test the change of default apache binding

    >>> cfg = os.path.join(recipe.options['prefix'], 'apache', 'vhost_www.mysite.com_81.conf')
    >>> print open(cfg).read()
    Listen *:81
    NameVirtualHost *:81
    ...



Rechange apache config::

   >>> options['bind_apache_http'] = '80'
   >>> recipe = Recipe(buildout, name, options)
   >>> paths = recipe.install()
   >>> cfg = os.path.join(recipe.options['prefix'], 'apache', 'vhost_www.mysite.com_80.conf')
   >>> print open(cfg).read()
   NameVirtualHost *:80
   ...

   >>> options['bind_apache_http'] = '192.168.2.1:80'
   >>> recipe = Recipe(buildout, name, options)
   >>> paths = recipe.install()
   >>> cfg = os.path.join(recipe.options['prefix'], 'apache', 'vhost_www.mysite.com_80.conf')
   >>> print open(cfg).read()
   Listen 192.168.2.1:80
   NameVirtualHost 192.168.2.1:80
   ...

View cache key generation config in apache::

   >>> print open(cfg).read()
   Listen 192.168.2.1:80
   ...
   <BLANKLINE>
       RewriteRule ^(.*)$ - [E=BACKEND_LOCATION:127.0.0.1]
       RewriteRule ^(.*)$ - [E=BACKEND_PORT:8080]
       RewriteRule ^(.*)$ - [E=BACKEND_PATH:mysite]
   <BLANKLINE>
       RewriteRule ^(.*)$ - [E=have_cookie:1]
       RewriteCond %{HTTP_COOKIE} my_key_one="([^"]+) [NC]
       RewriteRule ^(.*)$ - [E=my_key_one:%1]
       #test if have cookie
       RewriteCond %{HTTP_COOKIE} !^.*my_key_one.*$ [NC]
       RewriteRule ^(.*)$ - [E=have_cookie:0]
       RewriteCond %{HTTP_COOKIE} my_key_two="([^"]+) [NC]
       RewriteRule ^(.*)$ - [E=my_key_two:%1]
       #test if have cookie
       RewriteCond %{HTTP_COOKIE} !^.*my_key_two.*$ [NC]
       RewriteRule ^(.*)$ - [E=have_cookie:0]
       RewriteCond %{HTTP_COOKIE} my_key_three="([^"]+) [NC]
       RewriteRule ^(.*)$ - [E=my_key_three:%1]
       #test if have cookie
       RewriteCond %{HTTP_COOKIE} !^.*my_key_three.*$ [NC]
       RewriteRule ^(.*)$ - [E=have_cookie:0]
   <BLANKLINE>
       RewriteCond %{ENV:have_cookie} 1
       RewriteRule  ^/(.*)$ http://127.0.0.1:3128/%{ENV:BACKEND_LOCATION}/%{ENV:BACKEND_PORT}/https/%{SERVER_NAME}/80/%{ENV:BACKEND_PATH}/__zope_cache_key__/41d154089fd778d8efbd889dffc18dbd:%{ENV:my_key_one}:%{ENV:my_key_two}:%{ENV:my_key_three}/__cache_url__/$1 [L,P]
   <BLANKLINE>
       RewriteRule  ^/(.*)/$ http://127.0.0.1:3128/%{ENV:BACKEND_LOCATION}/%{ENV:BACKEND_PORT}/https/%{SERVER_NAME}/80/%{ENV:BACKEND_PATH}/__original_url__/$1 [L,P]
       RewriteRule  ^/(.*)$ http://127.0.0.1:3128/%{ENV:BACKEND_LOCATION}/%{ENV:BACKEND_PORT}/https/%{SERVER_NAME}/80/%{ENV:BACKEND_PATH}/__original_url__/$1 [L,P]
   ...

Now test a 2.6 config::

    >>> options['squid_version'] = '2.6'
    >>> buildout = {'instance': {'location': test_dir},
    ...             'buildout': {'directory': test_dir,
    ...                          'parts-directory': test_dir}}
    >>> name = 'squid'
    >>> recipe = Recipe(buildout, name, options)
    >>> recipe.options['squid_version']
    '2.6'
    >>> paths = recipe.install()
    >>> cfg = os.path.join(path, 'etc', 'squid.conf')



Test if redirector is threaded::

    >>> cfg = os.path.join(path, 'etc', 'iRedirector.py')
    >>> print open(cfg).read()
    #!...
    threaded =  1...

    >>> cfg = os.path.join(path, 'etc', 'squidAcl.py')
    >>> print open(cfg).read()
    #!...
    debug = 0...
    logfile = ...squid/log...

Change default location of installation::

    >>> options = {'url': 'mypackage.tgz', #url where we download squid src
    ...            'squid_owner': owner, #owner of squid process
    ...            'squid_group' : group, #group of squid process
    ...            'squid_port' : '3128', #listen port of proxy
    ...            'squid_version' : '2.5',
    ...            'squid_localisation': '127.0.0.1', #host or ip that apache use to request apache
    ...            'squid_log_dir' : '/var/log/dir',
    ...            'squid_config_dir' : '/usr/local/squid/etc',
    ...            'apache_conf_dir' : '/etc/apache2/conf',
    ...            'squid_admin_email' : 'myemail@mycompany.com', #name appear in error message
    ...            'squid_cache_size_mb' : '1000', #total cache in disk
    ...            'squid_visible_hostname' : 'mysite', #public name of your site, appear in error message
    ...            'front_https': '1', # does front server (apache, iis)
    ...                              # serve https url O by default
    ...            'front_http':'1', # does front server (apache, iis) serve http url
    ...            'debug_redirector':'1', #debug iRedirector 0 by default
    ...            'debug_squid_acl' : '0', #debug squidacl 0 by default
    ...            'debug_squid_rewrite_rules' : '1', #debug squidtrewriterule 0 by default
    ...
    ...           }

    >>> from iw.recipe.squid import Recipe

    >>> options['squid_accelerated_hosts'] = """
    ...    www.mysite.com: 127.0.0.1:8080/mysite
    ...    mysite.com: 127.0.0.1:8080/mysite
    ...    www.mysecondsite.com: 127.0.0.2:9080/mysite2
    ...    mysecondsite.com: 127.0.0.2:9080/mysite2
    ... """

    >>> recipe = Recipe(buildout, name, options)
    >>> recipe.options['apache_conf_dir']
    '/etc/apache2/conf'
    >>> recipe.options['squid_config_dir']
    '/usr/local/squid/etc'

