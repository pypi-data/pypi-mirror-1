#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

class EntityCfgParseError(Exception):
    pass
    
class Configuration(object):
    def __init__(self, cfg_file=None):
        self._c = ConfigParser.ConfigParser()
        if cfg_file:
            self._cfg_file = cfg_file
            try:
                self._read()
            except Exception, e:
                raise EntityCfgParseError

    def _read(self):
        try:
            self._c.read(self._cfg_file)
        except Exception, e:
            raise EntityCfgParseError, e
    
    def generate_default(self, filehandle=None, conf='basic'):
        def add_section(default_cfg, prefix, _name, **kw):
            settings = {}
            settings.update(kw)
            name = _name
            if prefix:
                name = "%s_%s" % (prefix, _name)
            default_cfg.add_section(name)
            for key in settings:
                default_cfg.set(name, key, settings[key])
            
        def add_worker(default_cfg, name, worker_binpath, binding, **kw):
            add_section(default_cfg, prefix="worker", 
                        _name=name, 
                        worker=worker_binpath, 
                        binding=binding,
                        numprocs=1,
                        listener='worker',
                        amqp='amqp',
                        **kw)
            
        default_cfg = ConfigParser.ConfigParser()
        
        # Add general section:        
        add_section(default_cfg, prefix=None, _name="general",
                    name='EntityStore',
                    base_url='http://my.entitystore.location/',
                    email='admin@foo.com')
                    
        # Add supervisor section:        
        add_section(default_cfg, prefix=None, _name="supervisor",
                    port='127.0.0.1:9001',
                    user='supervisor',
                    password='mypassword')
                    
        # Add base AMQP details
        add_section(default_cfg, prefix=None, _name="amqp",
                    type='StoreExchange',
                    host='localhost:5672',
                    userid='guest',
                    password='guest',
                    exchange='sqs_exchange')
        
        # Workers start with 'worker_' by convention
        # Logger is more for testing purposes - will be extrapolated
        # to being able to re-run sections of a queue later. 
        # For now, it's just a simpler logger.
        add_worker(default_cfg, 'accesslogger', 'workers/logger.py', '#.r',
                   logfile='logs/access.log')
        add_worker(default_cfg, 'changelogger', 'workers/logger.py', '#.w',
                   logfile='logs/change.log')
        add_worker(default_cfg, 'http4store', 'workers/http4store_loader.py', '#.w',
                   host='localhost:5000')
        
        stores = ['people']
        if conf == "all":
            stores = ['people', 'subjects', 'projects', 'groups', 'publications']
        
        for store in stores:
            add_section(default_cfg, prefix='store', _name=store,
                        type='filestore',
                        description='%s Store' % store.capitalize(),
                        amqp='amqp',
                        change_routingkey='%s.w' % store,
                        read_routingkey='%s.r' % store,
                        physical_dir='%s' % store,
                        uri_prefix='info:local/%s:' % store,
                        rest_suffix='%s' % store)
                
            add_worker(default_cfg, 
                       'solr_%s' % store, 
                       'workers/%s_loader.py' % store,
                       '%s.w' % store,
                       host='localhost:8080/solr/%s' % store)
                       
        if not filehandle:
            from StringIO import StringIO
            fakefile = StringIO()
            default_cfg.write(fakefile)
            fakefile.seek(0)
            return fakefile.read()
        else:
            default_cfg.write(filehandle)

if __name__ == '__main__':
    s = Configuration()
    import os
    import sys

    argv = sys.argv[1:]
    
    full = False
    overwrite = False
    conf = 'basic'
    
    if '--help' in argv:
        print """
        entityconfig.py [filename] {OPTIONS}
        
        If no filename is given, the output will be written to 'entitystore.cfg.default'
        
        Use --overwrite to allow the program to overwrite an existing file.
        
        Use --basic_conf [default] to get a basic EntityStore configuration, with just one
        store, one solr index and one 4Store index.
        
        Use --all_entities_conf to get a fuller EntityStore configuration, with a
        store and solr index for 5 types of entities and a 4Store index.
        """
    else:
        if len(argv) > 0:
            filename = argv.pop(0)
            if '--all' in argv:
                full = True
            if '--overwrite' in argv:
                overwrite = True
            if '--basic_conf' in argv:
                conf = 'basic'
            if '--all_entities_conf' in argv:
                conf = 'all'
        else:
            filename = 'entitystore.cfg.default'
            
        if not os.path.isfile(filename) or overwrite:
            fd = open(filename, 'wb')
            s.generate_default(filehandle=fd, conf=conf)
            fd.close()
        else:
            print "'entitystore.cfg.default' already exists\nSkipping saving.\n\nOutput on stdout:\n"
            print s.generate_default(conf=conf)
