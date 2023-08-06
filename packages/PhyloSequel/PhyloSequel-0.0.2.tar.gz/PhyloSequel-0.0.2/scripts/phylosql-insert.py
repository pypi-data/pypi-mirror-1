#! /usr/bin/env python

import sys
import os
import uuid
from optparse import OptionGroup
from optparse import OptionParser
from dendropy import datasets
from phylosequel.biosql import BioSql
from phylosequel import PACKAGE_VERSION as PHYLOSEQUEL_VERSION

_prog_usage = '%prog -d <engine://user:password@host:port/database> [options] <NeXML filepath>'
_prog_version = 'PhyloSequel Insert Version %s' % PHYLOSEQUEL_VERSION
_prog_description = 'inserts NeXML data into the specified database'
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
        
    parser.add_option('--ignore-missing',
        action='store_true',
        dest='ignore_missing',
        default=False,
        help='ignore missing file(s)')        
        
    parser.add_option('--verify',
        action='store_true',
        dest='verify',
        default=False,
        help='check all files for parse errors before importing any')    
                
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
        sys.stderr.write('NeXML file(s) to be imported need to be specified.\n')
        sys.exit(1)
    src_fpaths = []
    for a in args:
        f = os.path.expandvars(os.path.expanduser(a))
        if not os.path.exists(f):
            sys.stderr.write('File not found: "%s"\n' % f)
            if not opts.ignore_missing:
                sys.exit(1)
        elif not os.path.isfile(f):
            sys.stderr.write('Directory specified instead of file: "%s"\n' % f)
            if not opts.ignore_missing:
                sys.exit(1)
        else:
            src_fpaths.append(f)
            
    if len(src_fpaths) == 0:
        sys.stderr.write("No valid source files specified or found.\n")
        sys.exit(1)
        
    if opts.verify:
        for f in src_fpaths:
            if not opts.quiet:
                sys.stderr.write('Verifying: "%s"\n' % f)        
            d = datasets.Dataset()
            try:
                d.read(f, "nexml")
            except Exception, e:
                sys.stderr.write('Failed to parse: "%s"\n' % f)
                sys.stderr.write(str(e))
                sys.exit(1)
                
    ### dbengine ###
    if not opts.quiet:
        sys.stderr.write('Creating database engine ...\n')
    db = BioSql(opts.db_uri)
    db.echo = opts.echo
    

    biodb_id = db.get_biodb_id(opts.biodb_name, create=True)       
    nexml_edge_ontology_term_id = db.get_nexml_edge_term_id(create=True)
    nexml_node_otu_ontology_term_id = db.get_nexml_node_otu_term_id(create=True)
    session = db.create_session()
                                
    ### actual processing ###
    for f in src_fpaths:
        d = datasets.Dataset()
        if not opts.quiet:
            sys.stderr.write('Processing: "%s"\n' % f)
        try:
            d.read(f, "nexml")
        except Exception, e:
            sys.stderr.write('Failed to parse: "%s"\n' % f)
            sys.stderr.write(str(e))
            continue
                 
        for trees_block in d.trees_blocks:
            for tree in trees_block:
                name = str(uuid.uuid1())
                name = name[:32]
                if not opts.quiet:
                    sys.stderr.write('%s: TreeBlock [%s], Tree [%s] \n' % (f, trees_block.oid, tree.oid))
                    
                b_tree = BioSql.Tree(name, biodb_id, tree.label, tree.is_rooted)
                session.add(b_tree)
                session.flush()

                for node in tree.nodes():
                    b_node = BioSql.Node(b_tree.tree_id, node.label)
                    session.add(b_node)
                    session.flush()
                    node.biosql_node_id = b_node.node_id
                    
                    if node.taxon is not None:
                        b_otu = BioSql.Otu(node.taxon.label)
                        session.add(b_otu)
                        session.flush()
                        b_node_otu = BioSql.NodeOtu(b_node.node_id, 
                                                    b_otu.otu_id, 
                                                    nexml_node_otu_ontology_term_id)
                        session.add(b_node_otu)
                    
                for edge in tree.postorder_edge_iter():
                    if edge.tail_node and edge.head_node:
                        b_edge = BioSql.Edge(edge.tail_node.biosql_node_id, edge.head_node.biosql_node_id)
                        session.add(b_edge)
                        session.flush()
                        if edge.length is not None:
                            b_edge_term = BioSql.EdgeQualifierValue(b_edge.edge_id, nexml_edge_ontology_term_id, edge.length)
                            session.add(b_edge_term)
                    else:
                        pass
                        ### WHAT TO DO? NO 'ROOT EDGE' IN BIOSQL ###
                        
                b_tree.node_id = tree.seed_node.biosql_node_id
                
                if tree.is_rooted:
                    b_root = BioSql.TreeRoot(b_tree.tree_id, tree.seed_node.biosql_node_id)
                    session.add(b_root)
                
                session.commit()
                sys.stdout.write("%s\n" % b_tree.name)
                     
if __name__ == '__main__':
    main()

    
