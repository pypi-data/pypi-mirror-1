FILESTORAGE_TEMPLATE  = """\
    <filestorage>
      path $INSTANCE/var/%(file)s
    </filestorage>
    mount-point %(mountpoint)s
"""
ZEOCLIENT_TEMPLATE  = """\
   mount-point %(mountpoint)s
   cache-size %(cachesize)s
   <zeoclient>
     server %(server)s
     storage %(storage)s
     name zeostorage
     var $INSTANCE/var
     cache-size 20MB
   </zeoclient>
"""

clientpatterns = [
    {'type': 'line',
     'mode': 'replace',
     'pattern' : 'define HTTPPORT',
     'replace' : '%%define HTTPPORT %s\n',
     'option' : 'httpport'
    },
    {'type': 'line',
     'mode': 'replace',
     'pattern' : 'define ZOPE_USER',
     'replace' : '%%define ZOPE_USER %s\n',
     'option' : 'systemuser'
    },
    {'type': 'line',
     'mode': 'replace_or_add',
     'pattern' : 'zserver-threads ',
     'replace' : 'zserver-threads %s\n',
     'option' : 'threads',
    },
    {'type': 'line',
     'mode': 'replace_or_add',
     'pattern' : 'debug-mode ',
     'replace' : 'debug-mode %s\n',
     'option' : 'debugmode',
    },
    {'type': 'line',
     'mode': 'replace_or_add',
     'pattern' : 'verbose-security ',
     'replace' : 'verbose-security %s\n',
     'option' : 'verbosesecurity',
    },
    {'type': 'line',
     'mode': 'replace_or_add',
     'pattern' : 'security-policy-implementation ',
     'replace' : 'security-policy-implementation %s\n',
     'option' : 'securitypolicyimplementation',
    },
    {'type': 'line',
     'mode': 'replace_or_add',
     'pattern' : 'products ',
     'replace' : 'products %s',
     'optiontype': 'list',
     'option' : 'products',
    },
    {'type': 'sections',
     'mode': 'replace_or_add',
     'sectionname' : 'zodb_db',
     'optionprefix' : 'zodb_',
     'optiontype': 'dict',
     'templates': {'local': FILESTORAGE_TEMPLATE,
                   'zeo': ZEOCLIENT_TEMPLATE,},
    },    
]
