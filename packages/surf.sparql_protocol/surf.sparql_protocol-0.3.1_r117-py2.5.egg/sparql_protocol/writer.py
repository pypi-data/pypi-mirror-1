# Copyright (c) 2009, Digital Enterprise Research Institute (DERI),
# NUI Galway
# All rights reserved.
# author: Cosmin Basca
# email: cosmin.basca@gmail.com
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#    * Neither the name of DERI nor the
#      names of its contributors may be used to endorse or promote  
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY DERI ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DERI BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-
__author__ = 'Cosmin Basca, Adam Gzella'
    
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

from reader import ReaderPlugin
from surf.plugin.writer import RDFWriter
from surf.query.translator.sparul import SparulTranslator
from surf.query.update import insert, delete, clear

class WriterPlugin(RDFWriter):
    def __init__(self,reader,*args,**kwargs):
        RDFWriter.__init__(self,reader,*args,**kwargs)
        if isinstance(self.reader, ReaderPlugin):
            self.__endpoint         = self.reader.endpoint
            self.__default_graph    = self.reader.default_graph
        else:
            self.__endpoint         = kwargs['endpoint'] if 'endpoint' in kwargs else None
            self.__default_graph    = kwargs['default_graph'] if 'default_graph' in kwargs else None
            
        self.__results_format   = JSON
        
        print "endpoint: %s" % self.__endpoint
        self.__sparql_wrapper   = SPARQLWrapper(self.__endpoint, self.__results_format,defaultGraph=self.__default_graph)
                
    endpoint        = property(lambda self: self.__endpoint)
    default_graph   = property(lambda self: self.__default_graph)
            
    def _save(self, resource):
        s = resource.subject
        self.__remove(s)
        
        def statement_generator():
            for p, objs in resource.rdf_direct.items():
                for o in objs:
                    yield (s, p, o)
            
        self.__add_many(statement_generator())
    
    def _update(self, resource):
        s = resource.subject
        for p in resource.rdf_direct:
            self.__remove(s, p)
        for p, objs in resource.rdf_direct.items():
            for o in objs:
                self.__add(s, p, o)
    
    def _remove(self, resource, inverse = False):
        self.__remove(s=resource.subject)
        if inverse: self.__remove(o=resource.subject)
    
    def _size(self):
        '''
        Not implemented
        '''
        
        raise NotImplementedError
    
    def _add_triple(self,s=None,p=None,o=None,context = None):
        self.__add(s,p,o,context)
    
    def _set_triple(self,s=None,p=None,o=None,context = None):
        self.__remove(s,p,context=context)
        self.__add(s,p,o,context)
    
    def _remove_triple(self,s=None,p=None,o=None,context = None):
        self.__remove(s,p,o,context)

    def __add_many(self, triples, context = None):
        self.log.debug("ADD several triples")
        
        query = insert()

        graph = context if context != None else self.default_graph
        if graph:
            query.into(graph)
        
        for s, p, o in triples:
            query.template((s, p, o))
        
        try:
            query_str = SparulTranslator(query).translate()
            self.log.debug(query_str)
            self.__sparql_wrapper.setQuery(query_str)
            self.__sparql_wrapper.query().convert()
            return True
        except EndPointNotFound, notfound: 
            self.log.error('SPARQL ENDPOINT not found : \n' + str(notfound))
        except QueryBadFormed, badquery:
            self.log.error('SPARQL EXCEPTION ON QUERY (BAD FORMAT): \n ' + str(badquery))
        except SPARQLWrapperException, sparqlwrapper:
            self.log.error('SPARQL WRAPPER Exception \n' + str(sparqlwrapper))
        except Exception, e:
            self.log.error('Exception while querying' + str(e))

        return None

    
    def __add(self,s, p, o, context = None):
        return self.__add_many([(s, p, o)], context)
        
    def __remove(self,s=None,p=None,o=None,context=None):
        self.log.debug('REM : %s, %s, %s, %s' % (s, p, o, context))
        
        query = delete()
        graph = context if context != None else self.default_graph
        
        try:
            #clear
            if s == None and p == None and o == None and graph:
                query = clear().graph(graph)
            else:
                query = delete().from_(graph)
                query.template(("?s", "?p", "?o"))
                query.where(("?s", "?p", "?o"))
                query.filter("(" + self.__build_filter(s,p,o) + ")")
            
            query_str = SparulTranslator(query).translate()
            self.log.debug(query_str)
            self.__sparql_wrapper.setQuery(query_str)
            result = self.__sparql_wrapper.query().convert()
            return True
        except EndPointNotFound, notfound: 
            self.log.error('SPARQL ENDPOINT not found : \n' + str(notfound))
        except QueryBadFormed, badquery:
            self.log.error('SPARQL EXCEPTION ON QUERY (BAD FORMAT): \n ' + str(badquery))
        except SPARQLWrapperException, sparqlwrapper:
            self.log.error('SPARQL WRAPPER Exception \n' + str(sparqlwrapper))
        except Exception, e:
            self.log.error('Exception while querying' + str(e))

        return None
            
    def __build_filter(self,s,p,o):
        vars = [(s,'?s'),(p,'?p'),(o,'?o')]
        parts = []
        for var in vars:
            if var[0] != None:
                parts.append( "%s = %s"%(var[1],self._term(var[0]) ))
        
        return " and ".join(parts)
        
    def index_triples(self, **kwargs):
        '''
        performs index of the triples if such functionality is present,
        returns True if operation successfull
        '''
        
        # SPARQL/Update doesn't have standard way to force reindex. 
        return False
    
    def _clear(self, context = None):
        """ Clear the triple-store. """

        self.__remove(None, None, None)        
        
    def _term(self,term):
        if type(term) in [URIRef,BNode]:
            return '%s'%(term.n3())
        elif type(term) in [str, unicode]:
            if term.startswith('?'):
                return '%s'%term 
            elif is_uri(term):
                return '<%s>'%term 
            else:
                return '"%s"'%term
        elif type(term) is Literal:
            return term.n3()
        elif type(term) in [list,tuple]:
            return '"%s"@%s'%(term[0],term[1])
        elif type(term) is type and hasattr(term, 'uri'):
            return '%s'%term.uri().n3()
        elif hasattr(term, 'subject'):
            return '%s'%term.subject().n3()
        return term.__str__()        