import rdflib, sys
from rdflib.Graph import Graph
from rdflib.Collection import Collection
from n3 import parse, Tags

swapImplies = rdflib.URIRef('http://www.w3.org/2000/10/swap/log#implies')
owlSameAs = rdflib.URIRef('http://www.w3.org/2002/07/owl#sameAs')
rdfsType = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')

class GraphParser:
    def __init__(self, statements, prefixes={':': '#'}):
        self.statements = statements
        self.prefixes = prefixes
        self.bnodes = {}
        self.graph = Graph()
    
    def processGraph(self):
        for s in self.statements:
            if s in Tags.SimpleStatement: self.addPropertiesToNode(self.processPath(s[0]), s[1])
            elif s in Tags.Existential: pass
            elif s in Tags.Universal: pass
            elif s in Tags.PrefixDeclaration: self.prefixes[s[0]] = s[1]
        return self.graph
    
    def processPath(self, p):
        node = self.processNode(p[0])
        for o in zip(p[1::2], map(self.processNode, p[2::2])):
            newNode = rdflib.BNode()
            if o[0] == '!': self.graph.add((node, o[1], newNode))
            else: self.graph.add((newNode, o[1], node))
            node = newNode
        return node
    
    def processNode(self, n):
        if n in Tags.Literal: return rdflib.Literal(n[0])
        elif type(n) in (int, float, long): return rdflib.Literal(n)
        elif n in Tags.URI: return rdflib.URIRef(n)
        elif n in Tags.Qname and n[0] == '_:':
            if n[1] not in self.bnodes: self.bnodes[n[1]] = rdflib.BNode()
            return self.bnodes[n[1]]
        elif n in Tags.Qname: return rdflib.URIRef(self.prefixes[n[0] or ':'] + n[1])
        elif n in Tags.Variable: return rdflib.Variable(n)
        elif n in Tags.ThisNode: return self.graph
        elif n in Tags.PathListNode:
            b = rdflib.BNode()
            Collection(self.graph, b, map(self.processPath, n))
            return b
        elif n in Tags.PropertyListNode:
            b = rdflib.BNode()
            self.addPropertiesToNode(b, n)
            return b
        elif n in Tags.Formula:
            g = GraphParser(n, self.prefixes)
            return g.processGraph()
        
    def processVerb(self, v):
        active = v in Tags.Implies or v in Tags.SameAs or v in Tags.IsA or v in Tags.Path
        if v in Tags.ImpliedBy or v in Tags.Implies: return swapImplies, active
        elif v in Tags.SameAs: return owlSameAs, active #the funny joke is that sameAs is more like a copula, which is not really active nor passive lolololol
        elif v in Tags.IsA: return rdfsType, active
        elif v in Tags.Path or v in Tags.PassiveVerb: return self.processPath(v), active
        
    def addPropertiesToNode(self, node, propertyList):
        for verb, objects in propertyList:
            verb, active = self.processVerb(verb)
            objects = map(self.processPath, objects)
            for o in objects:
                if active: self.graph.add((node, verb, o))
                else: self.graph.add((o, verb, node))

if __name__ == '__main__':
    g = GraphParser(parse(sys.stdin.read())).processGraph()
    print g.serialize()
    #print '\n'.join(str(t) for t in g.triples((None, None, None)))