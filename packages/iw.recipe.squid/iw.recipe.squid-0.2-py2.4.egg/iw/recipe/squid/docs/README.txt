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
- squid_admin_email : email of the admin squid (by default webmaster@www.mysite.org)
- squid_cache_size_mb : size disk cache in mb (1000 by default)
- front_http : 1 by default (ie apache serve http request)
- front_https : 0 by default (ie apache serve https request)
- debug_redirector : 0 by default (ie debug squid redirector)
- debug_squid_acl : 0 by default (ie debug squid acl)
- debug_squid_rewrite_rules : 0 by default (ie debug squid acl)
- zope_cache_key : a list of zope cache key (if you want to cache specific
  zone of your site add specific acl)

buildout command create a directory structure like that::

    parts/squid/apache/vhost_www.mysite.org_80.conf : virtual host to include to apache
    parts/squid/etc/ : all config file for squid
    parts/squid/etc/squid.conf : main squid conf
    parts/squid/etc/iRedirector.py : to	launch squidRewriteRules
    parts/squid/etc/squidAcl.py	: avoid cache authenticated user by squid
    parts/squid/etc/squidRewriteRules.py : rewrite engine for squid
    parts/squid/cache/ : cache directory
    parts/squid/log/ : logs directory


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

    /usr/sbin/squid -z -f parts/squid/etc/squid.conf

To launch squid the generated config::

    /usr/sbin/squid -f parts/squid/etc/squid.conf

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
    ...		        'buildout': {'directory': test_dir,
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

    >>> paths = recipe.install()

Checking the files created::


    >>> paths
    '/.../tests/squid'

The default generated squid.conf
++++++++++++++++++++++++++++++++

    >>> cfg = os.path.join(paths, 'etc', 'squid.conf')
    >>> print open(cfg).read()
    # This configuration file requires squid 2.6+.  It is untested with squid 3.x.
    <BLANKLINE>
    # BASIC CONFIGURATION
    # ------------------------------------------------------------------------------
    <BLANKLINE>
    #  TAG: visible_hostname
    #   If you want to present a special hostname in error messages, etc,
    #   define this.  Otherwise, the return value of gethostname()
    #   will be used. If you have multiple caches in a cluster and
    #   get errors about IP-forwarding you must set them to have individual
    #   names with this setting.
    <BLANKLINE>
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
    cache_dir ufs .../iw/recipe/squid/tests/squid/cache 1000  16    256
    cache_mgr webmaster@www.mysite.com
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    # LOGS
    # ------------------------------------------------------------------------------
    log_icp_queries off
    cache_access_log .../iw/recipe/squid/tests/squid/log/access.log
    cache_log .../iw/recipe/squid/tests/squid/log/cache.log
    cache_store_log .../iw/recipe/squid/tests/squid/log/store.log
    # emulate_httpd_log off
    <BLANKLINE>
    <BLANKLINE>
    # RESOURCES
    # ------------------------------------------------------------------------------
    # amount of memory used for caching recently accessed objects - defaults to 8 MB
    cache_mem 64 MB
    maximum_object_size 10 MB       # max cached object size
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
    <BLANKLINE>
    acl accelerated_urls urlpath_regex ^/http/www.mysite.com/80/
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
    http_reply_access allow all
    <BLANKLINE>
    # Cache manager setup - cache manager can only connect from localhost
    # only allow cache manager access from localhost
    http_access allow manager localhost
    http_access deny manager
    # deny connect to other than ssl ports
    http_access deny connect !ssl_ports
    <BLANKLINE>
    # ICP access - anybody can access icp methods
    icp_access allow localhost
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
    redirect_program .../iw/recipe/squid/tests/squid/etc/iRedirector.py
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
    #
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
    <BLANKLINE>
    # 4) Prevent squid from caching requests from authenticated users or conditional
    # GETs with an If-None-Match header (since squid doesn't know about ETags)
    # We use an external python method to check these conditions and pass in the
    # value of the __ac cookie (two different ways to allow for different cookie
    # delimiters), the HTTP Authorization header, and the If-None-Match header.
    #
    # Squid caches the results of the external python method, so for debugging, set
    # the options ttl=0 negative_ttl=0 so you can see what is going on
    <BLANKLINE>
    # external_acl_type is_cacheable_type children=20 ttl=0 negative_ttl=0 %{Cookie:__ac} %{Cookie:;__ac} %{Authorization} %{If-None-Match} .../iw/recipe/squid/tests/squid/etc/squidAcl.py
    <BLANKLINE>
    external_acl_type is_cacheable_type protocol=2.5 children=20 %{Cookie:__ac} %{Cookie:;__ac} %{Authorization} %{If-None-Match} .../iw/recipe/squid/tests/squid/etc/squidAcl.py
    acl is_cacheable external is_cacheable_type
    no_cache allow is_cacheable
    <BLANKLINE>
    collapsed_forwarding on
    <BLANKLINE>
    # Explicitly disallow squid from handling anything else
    <BLANKLINE>
    <BLANKLINE>
    # 5) Specific zope cache keys
    <BLANKLINE>
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
    <BLANKLINE>
    <BLANKLINE>

The default generated squidRewriteRules.py
++++++++++++++++++++++++++++++++++++++++++


    >>> cfg = os.path.join(paths, 'etc', 'squidRewriteRules.py')
    >>> print open(cfg).read()
    #!...
    (r'http://127.0.0.1/http/www.mysite.com/80/(.*)',
    r'http://127.0.0.1:8080/VirtualHostBase/http/www.mysite.com:80/mysite/VirtualHostRoot/\1', 'P,L'),
    ...

The default generated conf for apache
+++++++++++++++++++++++++++++++++++++

    >>> cfg = os.path.join(paths, 'etc', 'squidRewriteRules.py')
    >>> print open(cfg).read()
    #!...

    >>> cfg = os.path.join(paths, 'apache', 'vhost_www.mysite.com_80.conf')
    >>> print open(cfg).read()
    NameVirtualHost *:80
    <VirtualHost *:80>
        ServerName www.mysite.com
        ServerAlias www.mysite.com
    <BLANKLINE>
        RewriteEngine On
        RewriteLog .../iw/recipe/squid/tests/squid/log/rewrite_www.mysite.com.log
        RewriteLogLevel 0
    <BLANKLINE>
        CustomLog .../iw/recipe/squid/tests/squid/log/access_www.mysite.com.log common
        ErrorLog .../iw/recipe/squid/tests/squid/log/error_www.mysite.com.log
    <BLANKLINE>
    <BLANKLINE>
        ## specific rules base on cookie
    <BLANKLINE>
    <BLANKLINE>
        ## common rules for squid rewrite rules
        RewriteRule  ^/(.*)/$ http://127.0.0.1:3128/http/%{SERVER_NAME}/80/$1 [L,P]
        RewriteRule  ^/(.*)$ http://127.0.0.1:3128/http/%{SERVER_NAME}/80/$1 [L,P]
    <BLANKLINE>
    <BLANKLINE>
    </VirtualHost>

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
    ...			   'front_https': '1', # does front server (apache, iis)
    ...                              # serve https url O by default
    ...			   'front_http':'1', # does front server (apache, iis) serve http url
    ...            'debug_redirector':'1', #debug iRedirector 0 by default
    ...            'debug_squid_acl' : '0', #debug squidacl 0 by default
    ...            'debug_squid_rewrite_rules' : '1', #debug squidtrewriterule 0 by default
    ...
    ...           }


Yours accelerated hosts ( zeo client or pound load balancer ,
urls to be accelerated wich corresponding of zope urls, ports, and directories)::

    >>> options['squid_accelerated_hosts'] = """
    ...	   www.mysite.com: 127.0.0.1:8080/mysite
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

    >>> print recipe.options['acl_accelerated_urls']
    acl accelerated_urls urlpath_regex ^/http/www.mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_one/http/www.mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_two/http/www.mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_three/http/www.mysite.com/80/
    acl accelerated_urls urlpath_regex ^/http/mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_one/http/mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_two/http/mysite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_three/http/mysite.com/80/
    acl accelerated_urls urlpath_regex ^/http/www.mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_one/http/www.mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_two/http/www.mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_three/http/www.mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/http/mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_one/http/mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_two/http/mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/my_key_three/http/mysecondsite.com/80/
    acl accelerated_urls urlpath_regex ^/https/www.mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_one/https/www.mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_two/https/www.mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_three/https/www.mysite.com/443/
    acl accelerated_urls urlpath_regex ^/https/mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_one/https/mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_two/https/mysite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_three/https/mysite.com/443/
    acl accelerated_urls urlpath_regex ^/https/www.mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_one/https/www.mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_two/https/www.mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_three/https/www.mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/https/mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_one/https/mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_two/https/mysecondsite.com/443/
    acl accelerated_urls urlpath_regex ^/my_key_three/https/mysecondsite.com/443/

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

    >>> paths
    '/.../tests/squid'


Checking the squid.conf created::

    >>> cfg = os.path.join(paths, 'etc', 'squid.conf')
    >>> print open(cfg).read()
    # This configuration file requires squid 2.5...

Checking if we have generate iRedirector conf::

    >>> cfg = os.path.join(paths, 'etc', 'iRedirector.py')
    >>> print open(cfg).read()
    #!...
    threaded =  0...

    >>> cfg = os.path.join(paths, 'etc', 'squidAcl.py')
    >>> print open(cfg).read()
    #!...



Now test a 2.6 config::

    >>> options['squid_version'] = '2.6'
    >>> buildout = {'instance': {'location': test_dir},
    ...		        'buildout': {'directory': test_dir,
    ...                          'parts-directory': test_dir}}
    >>> name = 'squid'
    >>> recipe = Recipe(buildout, name, options)
    >>> recipe.options['squid_version']
    '2.6'
    >>> paths = recipe.install()
    >>> cfg = os.path.join(paths, 'etc', 'squid.conf')

    >>> print open(cfg).read()
    # This configuration file requires squid 2.6...

Test if redirector is threaded::

    >>> cfg = os.path.join(paths, 'etc', 'iRedirector.py')
    >>> print open(cfg).read()
    #!...
    threaded =  1...

    >>> cfg = os.path.join(paths, 'etc', 'squidAcl.py')
    >>> print open(cfg).read()
    #!...
    debug = 0...
    logfile = ...squid/log...
