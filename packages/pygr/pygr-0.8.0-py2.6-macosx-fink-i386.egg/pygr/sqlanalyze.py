
from sqlgraph import *

def get_main_table(primaryKey, tset):
    'for a given primary key, pick the table that appears to be its main table'
    if len(tset)==1:
        return tset[0],[]
    for i,t in enumerate(tset):
        if t.name.split('.')[-1]+'_id'==primaryKey: # exon is main for exon_id
            return t,[x for x in tset if x is not t]
    l = [(len(t.description),t) for t in tset]
    l.sort()
    return l[-1],l[:-1] # assume the table with most columns is "main"

def table_graph(tables, idDict, joinTables=()):
    '''return graph structure for tables based on key structure.
    joinTables should be a dict of tables that each provide a many-to-many
    relation joining two tables.'''
    idMain = {}
    g = Graph()
    for primaryKey,tset in idDict.items(): # save 1:1 relations
        if len(tset)==0:
            continue
        main,others = get_main_table(primaryKey, tset)
        idMain[primaryKey] = main,others
        for t in others:
            g += main
            g[main][t] = '1:1',t
    for t in tables: # find foreign key relations
        l = []
        for f in t.description:
            try:
                if f!=t.primary_key and f in idDict:
                    raise AttributeError
            except AttributeError:
                l.append(f)
        if t in joinTables: # treat as many:many relation
            if len(l)!=2:
                raise ValueError('bad map %s:%s' % (t.name,l))
            main = idMain[l[0]][0]
            g += main
            g[main][idMain[l[1]][0]] = 'many:many',t
        else: # treat f:t as 1:many relation
            for f in l:
                if f in idMain:
                    g += idMain[f][0]
                    g[idMain[f][0]][t] = '1:many',t
    return idMain,g

def print_report(idMain, g):
    print '# TABLES'
    l = idMain.keys()
    l.sort()
    for primaryKey in l:
        print '########### Group: '+primaryKey
        t,tables = idMain[primaryKey]
        print t.name.split('.')[-1],':', t.description.keys(),'\n'
        for t in tables:
            print t.name.split('.')[-1],':', t.description.keys(),'\n'
        print '\n'
    print '\n\n# RELATIONS'
    for t1,d in g.items():
        for t2,(mapType,mapTable) in d.items():
            print '\t'.join([t1.name.split('.')[-1],t2.name.split('.')[-1],
                             mapType,mapTable.name.split('.')[-1]])
