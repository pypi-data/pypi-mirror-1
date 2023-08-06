#!/usr/bin/python
# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy, Error
from ConfigParser import ConfigParser, NoOptionError

class NotConnected(Exception):
    pass
class SupervisorNotConfigured(Exception):
    pass

class Supervisor_Control(object):
    def __init__(self, config):
        self.c = config
        self.conn = False

    def _write_supervisor_config(self, filepath):
        cfg = self.generate_supervisor_config()
        fd = open(filepath, 'wb')
        cfg.write(fd)
        fd.close()

    def generate_supervisor_config(self):
        if self.c and 'supervisor' in self.c.sections():
            s_cfg = ConfigParser()

            # Some hard defaults
            s_cfg.add_section('unix_http_server')
            s_cfg.set('unix_http_server', 'file', '/tmp/supervisor.sock')

            s_cfg.add_section('rpcinterface:supervisor')
            s_cfg.set('rpcinterface:supervisor',
                      'supervisor.rpcinterface_factory',
                      'supervisor.rpcinterface:make_main_rpcinterface')

            s_cfg.add_section('supervisorctl')
            s_cfg.set('supervisorctl',
                      'serverurl',
                      'unix:///tmp/supervisor.sock')

            # overriddable defaults
            inet_http_server = {'port':'127.0.0.1:9001',
                                'username':'guest',
                                'password':'guest'}

            supervisord = {'logfile':'/tmp/supervisord.log',
                           'logfile_maxbytes':'50MB',
                           'logfile_backups':'10',
                           'loglevel':'info',
                           'pidfile':'/tmp/supervisord.pid',
                           'nodaemon':'false',
                           'minfds':'1024',
                           'minprocs':'200'}

            cfg_sets = {'inet_http_server':inet_http_server,
                        'supervisord':supervisord,
                        }

            supervisor_params = dict(self.c.items('supervisor'))
            amqp_params = dict(self.c.items('amqp'))

            for cfg in cfg_sets:
                s_cfg.add_section(cfg)
                for key in cfg_sets[cfg]:
                    if key in supervisor_params:
                        cfg_sets[cfg][key] = supervisor_params[key]
                    s_cfg.set(cfg, key, cfg_sets[cfg][key])

            program_options = ['process_name','numprocs','directory','umask',
                               'priority','autostart','autorestart','startsecs',
                               'startretries','exitcodes','stopsignal',
                               'stopwaitsecs','user','redirect_stderr',
                               'stdout_logfile','stdout_logfile_maxbytes',
                               'stdout_logfile_backups','stdout_capture_maxbytes',
                               'stdout_events_enabled','stderr_logfile',
                               'stderr_logfile_maxbytes','stderr_logfile_backups',
                               'stderr_capture_maxbytes','stderr_events_enabled',
                               'environment','serverurl']

            for block in self.c.sections():
                if block.startswith('worker_') or block.startswith('service_'):
                    s_cfg.add_section('program:%s' % block)
                    worker = dict(self.c.items(block))

                    worker_settings = {'numprocs':1,
                                       'priority':'999',
                                       'autostart':'true',
                                       'autorestart':'true',
                                       'startsecs':'10',
                                       'startretries':'3',
                                       'stopwaitsecs':'10'
                                       }
                    for key in program_options:
                        if key in worker:
                            worker_settings[key] = worker[key]
                            del worker[key]
                        if key in worker_settings:
                            s_cfg.set('program:%s' % block,
                                      key,
                                      worker_settings[key])
                    # create command:
                    if 'command' not in worker:
                        commandline = worker['worker']
                        del worker['worker']

                        w_config = ConfigParser()
                        # Workers get there config in the [worker] section
                        # regardless of name
                        default_name = "worker"
                        w_config.add_section(default_name)
                        for (k,v) in worker.items():
                            if k == "amqp" and v in self.c.sections():
                                # Copy across amqp settings for each worker
                                w_config.add_section('amqp')
                                for (a,b) in self.c.items(v):
                                    w_config.set('amqp', a, b)
                            w_config.set(default_name, k, v)
                        fd = open('conf/%s.auto.conf' % block, 'wb')
                        w_config.write(fd)
                        fd.close()
                        s_cfg.set('program:%s' % block,
                                  'command',
                                  " ".join([commandline, 'conf/%s.auto.conf' % block]))
                    else:
                        s_cfg.set('program:%s' % block,
                                  'command',
                                  worker['command'])

            return s_cfg
        else:
            raise SupervisorNotConfigured()

    def update(self, config):
        self.c = config
        self.coldstart()

    def connect(self):

        self.conn = ServerProxy(self.s_url)

    def restart(self, soft=True):
        if not soft:
            return self.coldstart()
        elif self.conn:
            self.s.supervisor.restart()
        else:
            raise NotConnectedException()

    def shutdown(self):
        if self.conn:
            self.s.supervisor.shutdown()
        else:
            raise NotConnectedException()

    def coldstart(self):
        # TODO: Check for running instance
        # TODO: Shutdown instance if exists
        # TODO: Start supervisor daemon with config file
        pass


if __name__ == '__main__':
    import os
    import sys
    argv = sys.argv[1:]

    if '--help' in argv:
        print """
        workercontrol.py path/to/entitystore.cfg [path/to/supervisord config file]

        """
    else:
        filename = 'entitystore.cfg.default'
        conf = 'supervisord.conf'
        if len(argv) >= 1:
            filename = argv.pop(0)
            if len(argv) >= 1:
                conf = argv.pop(0)

        if not os.path.isfile(filename):
            print "Need to supply path for entitystore.cfg"
        else:
            cfg = ConfigParser()
            cfg_file = open(filename, 'rb')
            cfg.readfp(cfg_file)
            cfg_file.close()

            s = Supervisor_Control(cfg)
            s._write_supervisor_config(conf)

