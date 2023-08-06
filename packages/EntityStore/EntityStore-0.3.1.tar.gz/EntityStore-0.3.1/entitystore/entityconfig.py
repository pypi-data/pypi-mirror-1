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

    def generate_default(self, filehandle=None, conf='basic', 
                         store_base_url="http://localhost:8080/",
                         email='admin@foo.com', name='EntityStore', **general):
        def add_section(default_cfg, prefix, _name, **kw):
            settings = {}
            settings.update(kw)
            name = _name
            if prefix:
                name = "%s_%s" % (prefix, _name)
            default_cfg.add_section(name)
            for key in settings:
                default_cfg.set(name, key, settings[key])

        def add_service(default_cfg, name, service_binpath, **kw):
            add_section(default_cfg, prefix="service",
                        _name=name,
                        command=service_binpath,
                        **kw)
                        

        def add_worker(default_cfg, name, worker_binpath, numprocs=1, **kw):
            add_section(default_cfg, prefix="worker",
                        _name=name,
                        worker=worker_binpath,
                        numprocs=numprocs,
                        listener='worker',
                        **kw)

        default_cfg = ConfigParser.ConfigParser()

        # Add general section:
        add_section(default_cfg, prefix=None, _name="general",
                    base_url=store_base_url,
                    name=name,
                    email=email,
                    models="conf/models.cfg",
                    **general)

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

        # Add multicore solr and 4store services to supervisor list
        # Non-MQ run services start 'service_' by convention
        add_service(default_cfg, "Solr service", "services/solr.sh")
        add_service(default_cfg, "EntityStore web api", "./runme.py")
        add_service(default_cfg, "Redis service", "services/redis/redis-server services/redis/redis.conf")
        add_service(default_cfg, "4Store backend", "services/4store.sh")

        # Workers start with 'worker_' by convention
        # One 4store loader for all stores
        add_worker(default_cfg, 'http4store',
                   'workers/fourstore_loader.py',
                   binding="4store",
                   host='http://localhost:5000',
                   amqp="amqp",)

        stores = ['people']
        if conf == "all":
            stores = ['people', 'subjects', 'projects', 'groups', 'publications']

        for store in stores:
            add_section(default_cfg, prefix='store', _name=store,
                        type='filestore',
                        description='%s Store' % store.capitalize(),
                        amqp='amqp',
                        views='view_%s' % store,
                        change_routingkey='%s.w' % store,
                        read_routingkey='%s.r' % store,
                        physical_dir='%s' % store,
                        uri_prefix='%sstores/%s/objects/' % (store_base_url, store),
                        rest_suffix='%s' % store)

            add_section(default_cfg, prefix="view", _name=store,
                        objects="genericcontroller",
                        browse="%scontroller" % store)

            add_worker(default_cfg,
                       'solr_%s' % store,
                       'workers/solr_loader.py',
                       binding='solr_%s' % store,
                       model = store,
                       amqp="amqp",
                       title="%s Apache Solr search service" % store,
                       description="""Connection to the /search/ endpoint of this Solr index.
                       Default parameters are ?wt=json&amp;rows=10&amp;fl=*,score""",
                       service_suffix="solr_%s" % store,
                       register_get="http://localhost:8080/solr/%s/search?{q=Search Terms}" % store)

            add_worker(default_cfg,
                       'changemanager_%s' % store,
                       'workers/changemanager.py',
                       binding='%s.w' % store,
                       amqp="amqp",
                       fanout="solr_%s,4store" % store,
                       receipt_q = 'changemanager_%s' % store,
                       job_store = 'changemanager_%s' % store,
                       changelog='logs/%schange.log' % store,
                       accesslog='logs/%saccess.log' % store)

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

