#! /usr/bin/env python

###############################################################################
##  biosql.py
##
##  Part of the PhyloSequel BioSQL database toolkit.
##
##  Copyright 2009 Jeet Sukumaran.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

"""
Interactions with a BioSQL database.
"""

import sqlalchemy
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

class BioSql(object):
    """Wrapper for BioSQL database."""

    ##########################################################################
    ## Database Object Classes 
    
    class Biodatabase(object):
        def __init__(self, name, authority=None, description=None):
            self.name = name
            self.authority = authority
            self.description = description
            
    class Ontology(object):
        def __init__(self, name, definition=None):
            self.ontology_id = None
            self.name = name
            self.definition = definition
            
    class OntologyTerm(object):
        def __init__(self, ontology_id, name, definition=None, identifier=None):
            self.term_id = None
            self.ontology_id = ontology_id
            self.name = name
            self.definition = definition
            self.identifier = identifier
            
    class EdgeQualifierValue(object):
        def __init__(self, edge_id, term_id, value):
            self.edge_id = edge_id
            self.term_id = term_id
            self.value = value
            
    class Otu(object):
        def __init__(self, label):
            self.otu_id = None
            self.label = label
        
    class Tree(object):
        def __init__(self, 
                     name, 
                     biodatabase_id,
                     identifier=None,
                     is_rooted=False):
            self.tree_id = None
            self.name = name
            self.biodatabase_id = biodatabase_id
            self.identifier = identifier
            self.is_rooted = is_rooted
            self.node_id = -1                
    
    class Node(object):
        def __init__(self, tree_id, label):
            self.label = label
            self.tree_id = tree_id
    
    class Edge(object):
        def __init__(self, parent_node_id, child_node_id):
            self.parent_node_id = parent_node_id
            self.child_node_id = child_node_id
    
    class TreeRoot(object):
        def __init__(self, tree_id, node_id):
            self.tree_id = tree_id
            self.node_id = node_id
            
    class NodeOtu(object):
        def __init__(self, node_id, otu_id, term_id):
            self.node_id = node_id
            self.otu_id = otu_id
            self.term_id = term_id
           
    ##########################################################################
    ## INSTANCE METHODS - LIFECYCLE
            
    def __init__(self, db_uri):
        self.uri = None
        self.engine = None
        self.metadata = None
        self.session_factory = None
        self.tables = {
            'biodatabase' : BioSql.Biodatabase,
            'otu' : BioSql.Otu,
            'tree' : BioSql.Tree,
            'node' : BioSql.Node,
            'edge' : BioSql.Edge,
            'tree_root' : BioSql.TreeRoot,
            'ontology' : BioSql.Ontology,
            'term' : BioSql.OntologyTerm,
            'edge_qualifier_value' : BioSql.EdgeQualifierValue,
            'node_otu' : BioSql.NodeOtu
        }
        self.table_mappers = {}
        self.bind(db_uri)
        
    ##########################################################################
    ## INSTANCE PROPERTIES        
        
    def _get_echo(self):
        return self.engine.echo

    def _set_echo(self, val):
        self.engine.echo = val
        
    echo = property(_get_echo, _set_echo)      
           
    ##########################################################################
    ## INSTANCE METHODS - BINDINGS      
        
    def bind(self, db_uri):
        self.db_uri = db_uri
        self.engine = sqlalchemy.create_engine(self.db_uri)
        self.metadata = sqlalchemy.MetaData(self.engine)
        self.table_mappers = {}
        for table_name in self.tables:
            table_obj = sqlalchemy.Table(table_name, self.metadata, autoload=True)
            self.table_mappers[table_name] = mapper(self.tables[table_name], table_obj)
        self.session_factory = sessionmaker(bind=self.engine)
        
    def create_session(self):
        assert self.session_factory is not None
        return self.session_factory()
        
    ##########################################################################
    ## INSTANCE METHODS - PREPARING DATABASE FOR NEXML         
        
    def get_biodb_id(self, biodb_name, create=False):
        session = self.create_session()
        biodb_query = session.query(BioSql.Biodatabase).filter_by(name=biodb_name)
        biodb = biodb_query.first()
        if not biodb:
            if create:
                bd = BioSql.Biodatabase(biodb_name)
                session.add(bd)
                session.commit()
                return bd.biodatabase_id
            else:
                return None
        else:
            return biodb.biodatabase_id       
            
    def get_nexml_ontology_id(self, create=False):
        nexml_ontology_name = "NeXML"
        session = self.create_session()
        nexml_ontology_query = session.query(BioSql.Ontology).filter_by(name=nexml_ontology_name)
        nexml_ontology = nexml_ontology_query.first()
        if not nexml_ontology:
            if create:
                bd = BioSql.Ontology(nexml_ontology_name)
                session.add(bd)
                session.commit()
                return bd.ontology_id
            else:
                return None
        else:
            return nexml_ontology.ontology_id             
            
    def get_nexml_ontology_term_id(self, ontology_term, create=False):
        session = self.create_session()
        nexml_ontology_id = self.get_nexml_ontology_id(create)
        if not nexml_ontology_id:
            return None
        nexml_ontology_term_query = session.query(BioSql.OntologyTerm).filter_by(name=ontology_term)
        nexml_ontology_term = nexml_ontology_term_query.first()
        if not nexml_ontology_term:
            if create:
                bd = BioSql.OntologyTerm(nexml_ontology_id, ontology_term)
                session.add(bd)
                session.commit()
                return bd.ontology_id
            else:
                return None
        else:
            return nexml_ontology_term.ontology_id         
            
    def get_nexml_edge_term_id(self, create=False):
        return self.get_nexml_ontology_term_id("edge length", create)
        
    def get_nexml_node_otu_term_id(self, create=False):
        return self.get_nexml_ontology_term_id("node OTU", create)
