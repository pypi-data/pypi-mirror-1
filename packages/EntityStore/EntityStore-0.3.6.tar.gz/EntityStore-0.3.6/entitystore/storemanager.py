#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser, NoOptionError

from StringIO import StringIO

class Config(object):
    def __init__(self, name, *args, **kw):
        self._context = {}
        self._context['name'] = name
        self._context['args'] = args
        self._context['kw'] = kw
    def __setitem__(self, name, value):
        self._context[name] = value
    def __getitem__(self, name):
        return self._context[name]
    def keys(self):
        return self._context.keys()

class StoreConfigParser(object):
    def __init__(self, config=None):
        self.general = {}
        self.stores = {}
        if config:
            self._c = config
            self.parse_store_config()

    def parse_store_config(self, config = None):
        if config:
            self._c = config
        for block in self._c.sections():
            if block == 'general':
                # Do general stuff
                self.general = dict(self._c.items(block))
            elif block.startswith('store_'):
                """ [store_people]
                    change_routingkey = people.w
                    uri_prefix = info:local/people:
                    description = People Store
                    rest_suffix = people
                    type = filestore
                    physical_dir = people
                    read_routingkey = people.r
                    amqp = amqp"""
                configs = dict(self._c.items(block))
                s = Config(block[len('store_'):], **configs)
                if "views" in configs and configs["views"] in self._c.sections():
                    # Copy across amqp settings
                    views = Config(configs["views"], **dict(self._c.items(configs["views"])))
                    s['views'] = views
                if "amqp" in configs and configs["amqp"] in self._c.sections():
                    # Copy across amqp settings
                    amqp = Config(configs["amqp"], **dict(self._c.items(configs["amqp"])))
                    s['amqp'] = amqp
                self.stores[block[len('store_'):]] = s

    def keys(self):
        return self.stores.keys()

    def __getitem__(self, index):
        return self.stores[index]

    def parse_file(self, filepath):
        cfg = ConfigParser()
        cfg_file = open(filepath, 'rb')
        cfg.readfp(cfg_file)
        cfg_file.close()
        self.parse_store_config(cfg)

    def parse_string(self, bytestring):
        s = StringIO()
        s.write(bytestring)
        s.seek(0)
        cfg = ConfigParser()
        cfg.readfp(s)
        s.close()
        self.parse_store_config(cfg)

if __name__ == '__main__':
    import os
    import sys
    argv = sys.argv[1:]

    if '--help' in argv:
        print """
        workercontrol.py path/to/entitystore.cfg [path/to/supervisord config file]

        """
    else:
        sp = StoreConfigParser()
        if len(argv) >= 1:
            filename = argv.pop(0)
            if not os.path.isfile(filename):
                print "Need to supply path for entitystore.cfg"
            else:
                sp.parse_file(filename)
                print "Stores: %s" % sp.keys()
                print "=================================\n"
                for storename in sp.keys():
                    store = sp[storename]
                    print "Store name: %s" % store['name']
                    print "==========="
                    print "Config: %s" % store['name_value_pairs']
                    print "AMQP config: %s" % store['amqp']['name_value_pairs']
                    print "\n\n========================================="
        else:
            print "Need to supply path for entitystore.cfg"

