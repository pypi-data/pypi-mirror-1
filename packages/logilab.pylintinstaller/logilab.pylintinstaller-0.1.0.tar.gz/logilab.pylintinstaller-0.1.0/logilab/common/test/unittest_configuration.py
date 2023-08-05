import tempfile
import os
from cStringIO import StringIO
from sys import version_info

from logilab.common.testlib import TestCase, unittest_main
from logilab.common.configuration import Configuration, OptionValueError, \
     OptionsManagerMixIn, OptionsProviderMixIn, Method, read_old_config

options = [('dothis', {'type':'yn', 'default': True, 'metavar': '<y or n>'}),
           ('value', {'type': 'string', 'metavar': '<string>', 'short': 'v'}),
           ('multiple', {'type': 'csv', 'default': ('yop',),
                         'metavar': '<comma separated values>',
                         'help': 'you can also document the option'}),
           ('number', {'type': 'int', 'default':2, 'metavar':'<int>'}),
           ('choice', {'type': 'choice', 'default':'yo', 'choices': ('yo', 'ye'),
                       'metavar':'<yo|ye>'}),
           ('multiple-choice', {'type': 'multiple_choice', 'default':('yo', 'ye'),
                                'choices': ('yo', 'ye', 'yu', 'yi', 'ya'),
                                'metavar':'<yo|ye>'}),
           ('named', {'type':'named', 'default':Method('get_named'),
                      'metavar': '<key=val>'}),
           ]

class MyConfiguration(Configuration):
    """test configuration"""
    def get_named(self):
        return {'key': 'val'}
    
class ConfigurationTC(TestCase):
    
    def setUp(self):
        self.cfg = MyConfiguration(name='test', options=options, usage='Just do it ! (tm)')

    def test_default(self):
        cfg = self.cfg
        self.assertEquals(cfg['dothis'], True)
        self.assertEquals(cfg['value'], None)
        self.assertEquals(cfg['multiple'], ('yop',))
        self.assertEquals(cfg['number'], 2)
        self.assertEquals(cfg['choice'], 'yo')
        self.assertEquals(cfg['multiple-choice'], ('yo', 'ye'))
        self.assertEquals(cfg['named'], {'key': 'val'})

    def test_base(self):
        cfg = self.cfg
        cfg.set_option('number', '0')
        self.assertEquals(cfg['number'], 0)
        self.assertRaises(OptionValueError, cfg.set_option, 'number', 'youpi')
        self.assertRaises(OptionValueError, cfg.set_option, 'choice', 'youpi')
        self.assertRaises(OptionValueError, cfg.set_option, 'multiple-choice', ('yo', 'y', 'ya'))
        cfg.set_option('multiple-choice', 'yo, ya')
        self.assertEquals(cfg['multiple-choice'], ['yo', 'ya'])
        self.assertEquals(cfg.get('multiple-choice'), ['yo', 'ya'])
        self.assertEquals(cfg.get('whatever'), None)

    def test_load_command_line_configuration(self):
        cfg = self.cfg
        args = cfg.load_command_line_configuration(['--choice', 'ye', '--number', '4',
                                                    '--multiple=1,2,3', '--dothis=n',
                                                    'other', 'arguments'])
        self.assertEquals(args, ['other', 'arguments'])
        self.assertEquals(cfg['dothis'], False)
        self.assertEquals(cfg['multiple'], ['1', '2', '3'])
        self.assertEquals(cfg['number'], 4)
        self.assertEquals(cfg['choice'], 'ye')
        self.assertEquals(cfg['value'], None)
        args = cfg.load_command_line_configuration(['-v', 'duh'])
        self.assertEquals(args, [])
        self.assertEquals(cfg['value'], 'duh')
        self.assertEquals(cfg['dothis'], False)
        self.assertEquals(cfg['multiple'], ['1', '2', '3'])
        self.assertEquals(cfg['number'], 4)
        self.assertEquals(cfg['choice'], 'ye')
        
    def test_load_configuration(self):
        cfg = self.cfg
        args = cfg.load_configuration(choice='ye', number='4',
                                      multiple='1,2,3', dothis='n',
                                      multiple_choice=('yo', 'ya'))
        self.assertEquals(cfg['dothis'], False)
        self.assertEquals(cfg['multiple'], ['1', '2', '3'])
        self.assertEquals(cfg['number'], 4)
        self.assertEquals(cfg['choice'], 'ye')
        self.assertEquals(cfg['value'], None)
        self.assertEquals(cfg['multiple-choice'], ('yo', 'ya'))
        
    def test_generate_config(self):
        stream = StringIO()
        self.cfg.generate_config(stream)
        self.assertLinesEquals(stream.getvalue().strip(), """# test configuration
[TEST]

dothis=yes

#value=

# you can also document the option
multiple=yop

number=2

choice=yo

multiple-choice=yo,ye

named=key:val
""")
        
    def test_generate_config_with_space_string(self):
        self.cfg['value'] = '    '
        stream = StringIO()
        self.cfg.generate_config(stream)
        self.assertLinesEquals(stream.getvalue().strip(), """# test configuration
[TEST]

dothis=yes

value='    '

# you can also document the option
multiple=yop

number=2

choice=yo

multiple-choice=yo,ye

named=key:val
""")
        

    def test_loopback(self):
        cfg = self.cfg
        f = tempfile.mktemp()
        stream = open(f, 'w')
        try:
            cfg.generate_config(stream)
            stream.close()
            new_cfg = MyConfiguration(name='testloop', options=options)
            new_cfg.load_file_configuration(f)
            self.assertEquals(cfg['dothis'], new_cfg['dothis'])
            self.assertEquals(cfg['multiple'], new_cfg['multiple'])
            self.assertEquals(cfg['number'], new_cfg['number'])
            self.assertEquals(cfg['choice'], new_cfg['choice'])
            self.assertEquals(cfg['value'], new_cfg['value'])
            self.assertEquals(cfg['multiple-choice'], new_cfg['multiple-choice'])
        finally:
            os.remove(f)
        
    def test_help(self):
        self.cfg.add_help_section('bonus', 'a nice additional help')
        help = self.cfg.help().strip()
        # at least in python 2.4.2 the output is:
        # '  -v <string>, --value=<string>'
        # it is not unlikely some optik/optparse versions do print -v<string>
        # so accept both
        help = help.replace(' -v <string>, ', ' -v<string>, ')
        if version_info >= (2, 5):
            self.assertLinesEquals(help, """Usage: Just do it ! (tm)

Options:
  -h, --help            show this help message and exit
  --dothis=<y or n>     
  -v<string>, --value=<string>
  --multiple=<comma separated values>
                        you can also document the option [current: none]
  --number=<int>        
  --choice=<yo|ye>      
  --multiple-choice=<yo|ye>
  --named=<key=val>     

  Bonus:
    a nice additional help
""".strip())
        elif version_info >= (2, 4):
            self.assertLinesEquals(help, """usage: Just do it ! (tm)

options:
  -h, --help            show this help message and exit
  --dothis=<y or n>     
  -v<string>, --value=<string>
  --multiple=<comma separated values>
                        you can also document the option [current: none]
  --number=<int>        
  --choice=<yo|ye>      
  --multiple-choice=<yo|ye>
  --named=<key=val>     

  Bonus:
    a nice additional help
""".strip())
        else:
            self.assertLinesEquals(help, """usage: Just do it ! (tm)

options:
  -h, --help            show this help message and exit
  --dothis=<y or n>     
  -v<string>, --value=<string>
  --multiple=<comma separated values>
                        you can also document the option
  --number=<int>        
  --choice=<yo|ye>      
  --multiple-choice=<yo|ye>
  --named=<key=val>     

  Bonus:
    a nice additional help
""".strip())


    def test_manpage(self):
        from logilab.common import __pkginfo__
        self.cfg.generate_manpage(__pkginfo__, stream=StringIO())

    def test_rewrite_config(self):
        changes = [('renamed', 'renamed', 'choice'),
                   ('moved', 'named', 'old', 'test'),
                   ]
        read_old_config(self.cfg, changes, 'data/test.ini')
        stream = StringIO()
        self.cfg.generate_config(stream)
        self.assertLinesEquals(stream.getvalue().strip(), """# test configuration
[TEST]

dothis=yes

value='    '

# you can also document the option
multiple=yop

number=2

choice=yo

multiple-choice=yo,ye

named=key:val
""")
        
class Linter(OptionsManagerMixIn, OptionsProviderMixIn):
    options = (
        ('profile', {'type' : 'yn', 'metavar' : '<y_or_n>',
                     'default': False,
                     'help' : 'Profiled execution.'}),
        )
    def __init__(self):
        OptionsManagerMixIn.__init__(self, usage="")
        OptionsProviderMixIn.__init__(self)
        self.register_options_provider(self)
        self.load_provider_defaults()

class RegrTC(TestCase):

    def setUp(self):
        self.linter = Linter()
        
    def test_load_defaults(self):
        self.linter.load_command_line_configuration([])
        self.assertEquals(self.linter.config.profile, False)
        
        
if __name__ == '__main__':
    unittest_main()
