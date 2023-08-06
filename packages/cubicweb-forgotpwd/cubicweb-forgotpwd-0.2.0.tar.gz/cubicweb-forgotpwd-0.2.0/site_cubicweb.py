options = (
    ('revocation-limit',
     {'type' : 'int',
      'default': 30,
      'help': 'Forgot password link life time validity',
      'group': 'forgotpwd', 'inputlevel': 2,
      }),
    ('forgotpwd-cypher-seed',
     {'type' : 'string',
      'default': u"this is my dummy forgotpwd cypher seed",
      'help': 'seed used to cypher validation key sent in forgot password email link',
      'group': 'forgotpwd', 'inputlevel': 2,
      }),
    )
