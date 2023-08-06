#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

import re

from tempfile import mkstemp

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('modelloader')

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
        self.lookups = {}
        self.schemas = {}
        if fname:
            logger.info("Parsing the passed configuration file")
            self.parse(fname)

    def generate_solrschemas(self):
        header = """<?xml version="1.0" encoding="UTF-8" ?>
<schema name="%s" version="1.1">
  <types>
    <fieldType name="string" class="solr.StrField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="text" class="solr.TextField" positionIncrementGap="100">
      <analyzer type="index">
        <tokenizer class="solr.WhitespaceTokenizerFactory"/>
        <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="1" catenateNumbers="1" catenateAll="0" splitOnCaseChange="1"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.EnglishPorterFilterFactory" protected="protwords.txt"/>
        <filter class="solr.RemoveDuplicatesTokenFilterFactory"/>
      </analyzer>
      <analyzer type="query">
        <tokenizer class="solr.WhitespaceTokenizerFactory"/>
        <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="0" catenateNumbers="0" catenateAll="0" splitOnCaseChange="1"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.EnglishPorterFilterFactory" protected="protwords.txt"/>
        <filter class="solr.RemoveDuplicatesTokenFilterFactory"/>
      </analyzer>
    </fieldType>
    </types>"""
        footer = """
 <!-- Field to use to determine and enforce document uniqueness. 
      Unless this field is marked with required="false", it will be a required field
   -->
 <uniqueKey>id</uniqueKey>

 <!-- field for the QueryParser to use when an explicit fieldname is absent -->
 <defaultSearchField>text</defaultSearchField>

 <!-- SolrQueryParser configuration: defaultOperator="AND|OR" -->
 <solrQueryParser defaultOperator="OR"/>
</schema>"""
        for schema in self.mappings:
            fields = [header % schema]
            fields.append('<fields><field name="id" type="string" indexed="true"  stored="true"  multiValued="false" required="true"/><field name="text" type="text" indexed="true"  stored="true"  multiValued="true"/>')
            for field in self.mappings[schema]:
                # TODO enforce cardinality
                fields.append('<field name="%s" type="text" indexed="true"  stored="true"  multiValued="true"/>' % field)
            fields.append('</fields>')
            for field in self.mappings[schema]:
                fields.append('<copyField source="%s" dest="text"/>' % (field))
            fields.append(footer)
            self.schemas[schema] = "\n".join(fields)

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
            self.lookups[block] = {}
            for (k,v) in self._c.items(block):
                logger.debug("k = '%s', v = '%s' from %s" % (k,v,block))
                m = model_matcher.findall(v)
                if m != None:
                    logger.debug("Parsed '%s' to '%s'" % (v,m))
                    self.mappings[block][k] = m
                    for item in m:
                        self.lookups[block][item[0]] = (k, item[1], item[2])
                else:
                    logger.debug("Failed to parse '%s' against the regex" % (v))
                    self.mappings[block][k] = v
        return self.mappings

