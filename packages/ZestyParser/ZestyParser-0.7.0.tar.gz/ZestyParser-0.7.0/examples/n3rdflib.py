import rdflib, sys
from rdflib.Graph import Graph
from rdflib.Collection import Collection
from n3 import parse, AHT

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
            if type(s) is AHT.SimpleStatement: self.addPropertiesToNode(self.processPath(s[0]), s[1])
            elif type(s) is AHT.Existential: pass
            elif type(s) is AHT.Universal: pass
            elif type(s) is AHT.PrefixDeclaration: self.prefixes[s[0]] = s[1]
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
        if type(n) is AHT.Literal: return rdflib.Literal(n[0])
        elif type(n) in (int, float, long): return rdflib.Literal(n)
        elif type(n) is AHT.URI: return rdflib.URIRef(n)
        elif type(n) is AHT.Qname and n[0] == '_:':
            if n[1] not in self.bnodes: self.bnodes[n[1]] = rdflib.BNode()
            return self.bnodes[n[1]]
        elif type(n) is AHT.Qname: return rdflib.URIRef(self.prefixes[n[0] or ':'] + n[1])
        elif type(n) is AHT.Variable: return rdflib.Variable(n)
        elif type(n) is AHT.ThisNode: return self.graph
        elif type(n) is AHT.PathListNode:
            b = rdflib.BNode()
            Collection(self.graph, b, map(self.processPath, n))
            return b
        elif type(n) is AHT.PropertyListNode:
            b = rdflib.BNode()
            self.addPropertiesToNode(b, n)
            return b
        elif type(n) is AHT.Formula:
            g = GraphParser(n, self.prefixes)
            return g.processGraph()
        
    def processVerb(self, v):
        active = type(v) in (AHT.Implies, AHT.SameAs, AHT.IsA, AHT.Path)
        if type(v) in (AHT.ImpliedBy, AHT.Implies): return swapImplies, active
        elif type(v) is AHT.SameAs: return owlSameAs, active #the funny joke is that sameAs is more like a copula, which is not really active nor passive lolololol
        elif type(v) is AHT.IsA: return rdfsType, active
        elif type(v) in (AHT.Path, AHT.PassiveVerb): return self.processPath(v), active
        
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