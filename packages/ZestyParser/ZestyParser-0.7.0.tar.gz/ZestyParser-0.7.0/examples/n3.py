from ZestyParser import *
import sys

AHT = AHT.Env()

ign = Skip(TokenSeries(Token('#[^\n]*\n') | Token('\s+'), min=1))
igns = ign.pad
t_name = Token('(?=\w)[^\d]\w*', group=0)
t_uri = Token('<([^>]*)>', group=1, to=AHT.URI)
t_prefix = Token('(?:(?=\w)[^\d]\w*)?:', group=0, to=AHT.Prefix)
t_qname = ((t_prefix | EmptyToken) + t_name) >> AHT.Qname

t_symbol = t_uri | t_qname
t_symbol_list = TokenSeries(t_symbol, skip=ign, delimiter=RawToken(','))
t_prefix_decl = igns(Omit(RawToken('@prefix')) + t_prefix + t_uri) >> AHT.PrefixDeclaration
t_keywords_decl = igns(Omit(RawToken('@keywords')) + TokenSeries(t_name, skip=ign, delimiter=RawToken(','))) >> AHT.KeywordsDeclaration
t_existential = igns(RawToken('@forSome') + Only(t_symbol_list)) >> AHT.Existential
t_universal = igns(RawToken('@forAll') + Only(t_symbol_list)) >> AHT.Universal

t_literal = igns(
    (
        Token(r'"""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""', group=0, to=eval) |
        Token(r'"[^"\\]*(?:\\.[^"\\]*)*"', group=0, to=eval)
    ) +
    (
        igns(Omit(RawToken('@')) + Token('[a-z]+(-[a-z0-9]+)*', group=0)) |
        igns(Omit(RawToken('^^')) + t_symbol) |
        Default(None)
    )
) >> AHT.Literal

t_numeric_literal = Token(r'[-+]?[0-9]+(\.[0-9]+)?(e[-+]?[0-9]+)?', group=0, to=eval)
t_this = RawToken('@this', to=AHT.ThisNode)
t_variable = Token('\?((?=\w)[^\d]\w*)', group=1, to=AHT.Variable)

t_node = t_literal | t_numeric_literal | t_symbol | t_variable | t_this | Defer(lambda:t_path_list) | Defer(lambda:t_property_list_node) | Defer(lambda:t_formula)

t_path = TokenSeries(t_node, skip=ign, delimiter=(RawToken('!') | RawToken('^')), includeDelimiter=True, min=1, to=AHT.Path)
t_path_list = (RawToken('(') + Only(TokenSeries(t_path, skip=ign)) + RawToken(')')) >> AHT.PathListNode

t_verb = (
    RawToken('<=', to=AHT.ImpliedBy) |
    RawToken('=>', to=AHT.Implies) |
    RawToken('=', to=AHT.SameAs) |
    RawToken('a', to=AHT.IsA) |
    igns(RawToken('has') + Only(t_path)) |
    (
        igns(RawToken('is') + Only(t_path) + RawToken('of'))
        >> AHT.PassiveVerb
    ) |
    t_path
)

t_property_list = TokenSeries(
    (t_verb + TokenSeries(t_path, skip=ign, delimiter=RawToken(','))),
    delimiter=RawToken(';'), skip=ign
)

t_property_list_node = igns(
    RawToken('[') + 
    Only(t_property_list ^ 'Expected property list') + 
    RawToken(']')
) >> AHT.PropertyListNode

t_simple_statement = igns(
    t_path + (t_property_list ^ 'Expected property list')
) >> AHT.SimpleStatement

t_statement = t_simple_statement | t_existential | t_universal \
    | t_prefix_decl | t_keywords_decl 

t_statement_list = (
    Only(TokenSeries(t_statement, delimiter=RawToken('.'), skip=ign)) + 
    Skip(RawToken('.'))
) >> AHT.StatementList

t_formula = (
    RawToken('{') +
    Only(t_statement_list ^ 'Expected statements') +
    (RawToken('}') ^ 'Expected }')
) >> AHT.Formula

t_document = (
    ign + Only(t_statement_list) + ign +
    (EOF ^ 'Expected end of input')
)

def parse(string):
    return ZestyParser(string).scan(t_document)

if __name__ == '__main__':
    print parse(sys.stdin.read())