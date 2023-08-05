from ZestyParser import *
from ZestyParser.Helpers import *
import sys

ign = Skip((RE('#[^\n]*\n') | RE('\s+'))*(1, Inf))

t_name = RE('(?=\w)[^\d]\w*', group=0)
t_uri = RE('<([^>]*)>', group=1, to=Tags.URI)
t_prefix = RE('(?:(?=\w)[^\d]\w*)?:', group=0, to=Tags.Prefix)
t_qname = ((t_prefix | EmptyToken) + t_name) >> Tags.Qname

t_symbol = t_uri | t_qname
t_symbol_list = TokenSeries(t_symbol, skip=ign, delimiter=Raw(','))
t_prefix_decl = (Omit(Raw('@prefix')) - t_prefix - t_uri) >> Tags.PrefixDeclaration
t_keywords_decl = Raw('@keywords') - Only(TokenSeries(t_name, skip=ign, delimiter=Raw(','), to=Tags.KeywordsDeclaration))
t_existential = (Raw('@forSome') - Only(t_symbol_list)) >> Tags.Existential
t_universal = (Raw('@forAll') - Only(t_symbol_list)) >> Tags.Universal

t_literal = (
    (
        RE(r'"""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""', group=0, to=eval) |
        RE(r'"[^"\\]*(?:\\.[^"\\]*)*"', group=0, to=eval)
    ) -
    (
        (Omit(Raw('@')) - RE('[a-z]+(-[a-z0-9]+)*', group=0)) |
        (Omit(Raw('^^')) - t_symbol) |
        Default(None)
    )
) >> Tags.Literal

t_numeric_literal = RE(r'[-+]?[0-9]+(\.[0-9]+)?(e[-+]?[0-9]+)?', group=0, to=eval)
t_this = Raw('@this', to=Tags.ThisNode)
t_variable = RE('\?((?=\w)[^\d]\w*)', group=1, to=Tags.Variable)

t_node = t_literal | t_numeric_literal | t_symbol | t_variable | t_this | Placeholder() | Placeholder() | Placeholder()

t_path = TokenSeries(t_node, skip=ign, delimiter=(Raw('!') | Raw('^')), includeDelimiter=True, min=1, to=Tags.Path)
t_path_list = EncloseHelper('()', TokenSeries(t_path, skip=ign), to=Tags.PathListNode)

t_verb = (
    Raw('<=', to=Tags.ImpliedBy) |
    Raw('=>', to=Tags.Implies) |
    Raw('=', to=Tags.SameAs) |
    Raw('a', to=Tags.IsA) |
    (Raw('has') - Only(t_path)) |
    ((Raw('is') - Only(t_path) - Raw('of')) >> Tags.PassiveVerb) |
    t_path
)

t_property_list = TokenSeries(
    (t_verb + TokenSeries(t_path, skip=ign, delimiter=Raw(','))),
    delimiter=Raw(';'), skip=ign
) ^ 'Expected property list'

t_property_list_node = EncloseHelper('[]', t_property_list, to=Tags.PropertyListNode)

t_simple_statement = (t_path - t_property_list) >> Tags.SimpleStatement

t_statement = (t_simple_statement | t_existential | t_universal
    | t_prefix_decl | t_keywords_decl)

t_statement_list = (
    Only(TokenSeries(t_statement, delimiter=Raw('.'), skip=ign))+Skip(Raw('.'))
) >> Tags.StatementList

t_formula = EncloseHelper('{}', t_statement_list ^ 'Expected statements', to=Tags.Formula)

t_node %= [t_path_list, t_property_list_node, t_formula]

t_document = ign + Only(t_statement_list) - (EOF ^ 'Expected end of input')

def parse(string):
    p = ZestyParser(string)
    p.whitespace = ign
    return p.scan(t_document)

if __name__ == '__main__':
    print parse(sys.stdin.read())