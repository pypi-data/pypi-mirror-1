#! /usr/bin/env python
#! /usr/bin/env python

import sys
import os
import uuid
from optparse import OptionGroup
from optparse import OptionParser
from dendropy import datasets
from dendropy import trees
from phylosequel.biosql import BioSql
from phylosequel import PACKAGE_VERSION as PHYLOSEQUEL_VERSION

_prog_usage = '%prog -d <engine://user:password@host:port/database> [options] <NAME>'
_prog_version = 'PhyloSequel GetTree Version %s' % PHYLOSEQUEL_VERSION
_prog_description = 'retrieves a tree by name'
_prog_author = 'Jeet Sukumaran'

def main():
    """
    Main CLI handler.
    """
    
    parser = OptionParser(usage=_prog_usage, 
        add_help_option=True, 
        version=_prog_version, 
        description=_prog_description)    
       
    parser.add_option('-d', '--database',
        action='store',
        dest='db_uri',
        type='string', # also 'float', 'string' etc.
        default=None,
        metavar='URI',
        help='[MANDATORY] database URI (e.g. "postgres://scott:tiger@localhost/demodb")')
        
    parser.add_option('-b', '--biodatabase',
        action='store',
        dest='biodb_name',
        type='string', # also 'float', 'string' etc.
        default="dbhack1",
        metavar='NAME',
        help='namespace for this table [default="%default"]')        

#     parser.add_option('-b', '--biodatabase',
#         action='store',
#         dest='biodb_name',
#         type='string', # also 'float', 'string' etc.
#         default="dbhack1",
#         metavar='NAME',
#         help='namespace for this table [default="%default"]')
#         
#     parser.add_option('--ignore-missing',
#         action='store_true',
#         dest='ignore_missing',
#         default=False,
#         help='ignore missing file(s)')        
#         
#     parser.add_option('--verify',
#         action='store_true',
#         dest='verify',
#         default=False,
#         help='check all files for parse errors before importing any')

    parser.add_option('--newick',
        action='store_true',
        dest='newick',
        default=False,
        help='output newick string [default = NeXML]') 
        
    parser.add_option('--nexus',
        action='store_true',
        dest='nexus',
        default=False,
        help='output NEXUS file [default = NeXML]')         
                
    parser.add_option('-q', '--quiet',
        action='store_true',
        dest='quiet',
        default=False,
        help='suppress progress messages')  
        
    parser.add_option('-e', '--echo',
        action='store_true',
        dest='echo',
        default=False,
        help='echo database communications')
                      
    (opts, args) = parser.parse_args()

    if opts.db_uri is None:
        sys.stderr.write('Database URI needs to be specified ("-d" flag; see "--help").\n')
        sys.exit(1)
        
    if len(args) == 0:
        sys.stderr.write("Tree needs to be specified by name.\n")
        sys.exit(1)        
        
    ### dbengine ###
    if not opts.quiet:
        sys.stderr.write('Creating database engine ...\n')
    db = BioSql(opts.db_uri)
    db.echo = opts.echo
    session = db.create_session()      

    biodb_name = opts.biodb_name
    tree_name = args[0]
    biodb_query = session.query(BioSql.Biodatabase).filter_by(name=biodb_name)
    biodb = biodb_query.first()
    if not biodb:
        sys.stderr.write('Biodatabase "%s" not found.\n' % biodb_name)
        sys.exit(1)

    nexml_edge_ontology_term_id = db.get_nexml_edge_term_id(create=True)        
    
    if not opts.quiet:
        sys.stderr.write('Retrieving tree ...\n')        
    tree_query =  session.query(BioSql.Tree).filter_by(name=tree_name)      
    b_tree = tree_query.first()
    if not b_tree:
        sys.stderr.write('Tree "%s" not found in biodatabase "%s".\n' % (tree_name, biodb_name))
        sys.exit(1)
                
    ds = datasets.Dataset()
    taxa_block = ds.add_taxa_block()
    trees_block = ds.add_trees_block(taxa_block=taxa_block)    
    node_query = session.query(BioSql.Node).filter_by(tree_id=b_tree.tree_id)
    b_nodes = node_query.all()
    if len(b_nodes) == 0:
        sys.stderr.write('No nodes found belonging to "%s".\n' % tree_name)
        sys.exit(1)
        
    nodes = []
    parent_node_ids = {}
    id_node_map = {}
    for b_node in b_nodes:
        node = trees.Node(oid="n" + str(b_node.node_id))
        nodes.append(node)
        id_node_map[b_node.node_id] = node
        
        node_otu_query = session.query(BioSql.NodeOtu).filter_by(node_id=b_node.node_id)
        node_otus = node_otu_query.all()
        if len(node_otus) > 1:
            sys.stderr.write('Multiple otu\'s found in node "%s".\n'  % (b_node.node_id))
            sys.exit()
        elif len(node_otus) == 1:
            node_otu = node_otus[0]
            otu_query = session.query(BioSql.Otu).filter_by(otu_id=node_otu.otu_id)
            otu = otu_query.one()
            taxon = taxa_block.get_taxon(label=otu.label)
            node.taxon = taxon
        if b_node.label:
            node.label = b_node.label
#             taxon = taxa_block.get_taxon(label=b_node.label)
#             node.taxon = taxon
        b_edge_query = session.query(BioSql.Edge).filter_by(child_node_id=b_node.node_id)
        b_edges = b_edge_query.all()
        if len(b_edges) == 0:
#             sys.stderr.write('Warning: no edge for node "%s".\n' % b_node.node_id)
            pass
        elif len(b_edges) > 1:
            sys.stderr.write('Error: multiple edges returned for node "%s".\n' % b_node.node_id)
            sys.exit(1)
        else:            
            b_edge = b_edges[0]
            parent_node_ids[node] = b_edge.parent_node_id
            node.biosql_edge_id = b_edge.edge_id
            
            b_edge_len_query = session.query(BioSql.EdgeQualifierValue).filter_by(edge_id=b_edge.edge_id, 
                    term_id=nexml_edge_ontology_term_id, rank=0)
            b_edge_lens = b_edge_len_query.all()
            if len(b_edge_lens) > 1:
                sys.stderr.write('Multiple edge lengths returns for edge "%s".\n' % b_edge.edge_id)
                sys.exit(1)
            elif len(b_edge_lens) == 1:
                node.biosql_edge_len = b_edge_lens[0].value
            
    parentless_nodes = []            
    for node in nodes:
        if node in parent_node_ids:
            parent_id = parent_node_ids[node]
            if parent_id in id_node_map:
                parent_node = id_node_map[parent_id]
                parent_node.add_child(node)
                node.edge.length = node.biosql_edge_len
            else:
                sys.stderr.write('Parent node "%s" not found.\n' % parent_id)
                sys.exit(1)
        else:
            parentless_nodes.append(node)
    
    if len(parentless_nodes) == 0:
        sys.stderr.write("Cyclic error: every node has parent.\n")
        sys.exit(1)
    elif len(parentless_nodes) > 1:
        sys.stderr.write("Unconnected error: multiple nodes without parent.\n")
        sys.exit(1)
    else:
        tree = trees.Tree()
        tree.is_rooted = b_tree.is_rooted
        tree.oid = biodb_name + "_" + b_tree.name
        tree.label = str(b_tree.tree_id) + "_" + str(b_tree.identifier)
        tree.taxa_block = taxa_block
        tree.seed_node = parentless_nodes[0]
        
    trees_block.append(tree)        
    if opts.newick:
        ds.write(sys.stdout, "newick")
    elif opts.nexus:
        ds.write(sys.stdout, "nexus")
    else:
        ds.write(sys.stdout, "nexml")
                
if __name__ == "__main__":
    main()
    
    
    