#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

import re

from tempfile import mkstemp

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('checkm')

# Matches the following:
# http://example.org/terms/foo, l
model_matcher = re.compile(r"""(?P<uri>[^,^\;]+)
                               ,\s*
                               (?P<objtype>[lu])
                               (?:,\s*           # Set up the optional cardinality group, but don't retrieve it all
                               (?P<card>[\d]+)
                               )?\s*\;?
                            """, re.I|re.U|re.VERBOSE)

class ModelLoader(object):
    def __init__(self, fname=None):
        self._c = ConfigParser.ConfigParser()
        self.mappings = {}
        if fname:
            logger.info("Parsing the passed configuration file")
            self.parse(fname)

    def parse(self, fname):
        filename = fname
        tempfile = False
        if hasattr(fname, 'read'):
            logger.debug("File object has a 'read' attribute - will store this in a temporary file, and pass the temp filename to the ConfigParser instance")
            (fd, filename) = mkstemp()
            fh = os.fdopen(fd, "w")
            fh.write(fname.read())
            fh.close()
            tempfile = True
        self._c.read(filename)
        logger.info("Parsed the configuration file %s" % filename)
        if '_ns' in self._c.sections():
            logger.info("Found special '_ns' block - creating prefix to namespace mapping in key '_ns'")
            self.mappings['_ns'] = {}
            for (k,v) in self._c.items('_ns'):
                if v:
                    logger.debug("Mapping prefix '%s' to ns '%s'" % (k,v.strip()))
                    self.mappings['_ns'][k] = v.strip()
        else:
            logger.info("Did not find special '_ns' block containing prefix to namespace mappings...")
        for block in [x for x in self._c.sections() if x != '_ns']:
            logger.debug("Walking through %s of the models configuration file %s" % (block, filename))
            self.mappings[block] = {}
            for (k,v) in self._c.items(block):
                logger.debug("k = '%s', v = '%s' from %s" % (k,v,block))
                m = model_matcher.findall(v)
                if m != None:
                    logger.debug("Parsed '%s' to '%s'" % (v,m))
                    self.mappings[block][k] = m
                else:
                    logger.debug("Failed to parse '%s' against the regex" % (v))
                    self.mappings[block][k] = v
        return self.mappings

