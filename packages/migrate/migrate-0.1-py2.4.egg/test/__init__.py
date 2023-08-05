import fixture
__all__=[
    'shell',
    'cfgparse',
    'repository',
    'script',
    'template',
    'pathed',
    'version',
    'database',
    'controlled',
    'shell_runner',
    'unique_instance',
    'runchangeset',
    'logengine',
    'changeset',
    'constraint',
    'logchangeset',
]

# for setuptools
suite = fixture.suite(map((lambda x: __name__+'.'+x),__all__))

if __name__=='__main__':
    fixture.main(__all__)
