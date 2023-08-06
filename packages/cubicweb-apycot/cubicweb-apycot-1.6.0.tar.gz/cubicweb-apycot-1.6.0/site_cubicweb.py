# register severity sorting registered procedure
from rql.utils import register_function, FunctionDescr


class severity_sort_value(FunctionDescr):
    supported_backends = ('postgres', 'sqlite',)
    rtype = 'Int'

try:
    register_function(severity_sort_value)
except AssertionError:
    pass



try:
    from cubicweb.server import SQL_CONNECT_HOOKS
except ImportError: # no server installation
    pass
else:

    def init_sqlite_connexion(cnx):
        def severity_sort_value(text):
            return {"DEBUG": 0, "INFO": 10, "WARNING": 20,
                    "ERROR": 30, "FATAL": 40}[text]
        cnx.create_function("SEVERITY_SORT_VALUE", 1, severity_sort_value)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault('sqlite', [])
    sqlite_hooks.append(init_sqlite_connexion)


options = (
    ('bot-pyro-id',
     {'type' : 'string',
      'default' : ':apycot.apycotbot',
      'help': _('Identifier of the apycot bot in the pyro name-server.'),
      'group': 'apycot', 'inputlevel': 1,
      }),
    ('bot-pyro-ns',
     {'type' : 'string',
      'default' : None,
      'help': _('Pyro name server\'s host where the bot is registered. If not '
                'set, will be detected by a broadcast query. You can also '
                'specify a port using <host>:<port> notation.'),
      'group': 'apycot', 'inputlevel': 1,
      }),
    )
