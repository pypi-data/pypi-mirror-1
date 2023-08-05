from ZestyParser import *
import sys

AHT = AHT.Env()

IGN = Skip(TokenSeries(Token('#[^\n]*\n') | Token('\s+'), min=1))
T_BARENAME = Token('(?=\w)[^\d]\w*', group=0, as=AHT.Name)
T_EXPLICIT_URI = Token('<([^>]*)>', group=1, as=AHT.URI)
T_PREFIX = Token('(?:(?=\w)[^\d]\w*)?:', group=0, as=AHT.Prefix)
T_QNAME = ((T_PREFIX | EmptyToken) + T_BARENAME) >> AHT.Qname
T_LANGCODE = Token('[a-z]+(-[a-z0-9]+)*', group=0, as=AHT.LangCode)

T_SYMBOL = T_EXPLICIT_URI | T_QNAME
T_SYMBOL_LIST = TokenSeries(T_SYMBOL, skip=IGN, delimiter=RawToken(','))
T_PREFIX_DECLARATION = (Omit(RawToken('@prefix')) + IGN + T_PREFIX + IGN + T_EXPLICIT_URI) >> AHT.PrefixDeclaration
T_KEYWORDS_DECLARATION = (Omit(RawToken('@keywords')) + IGN + TokenSeries(T_BARENAME, skip=IGN, delimiter=RawToken(','))) >> AHT.KeywordsDeclaration
T_EXISTENTIAL = (Omit(RawToken('@forSome')) + IGN + T_SYMBOL_LIST) >> (lambda r: AHT.Existential(r[0]))
T_UNIVERSAL = (Omit(RawToken('@forAll')) + IGN + T_SYMBOL_LIST) >> (lambda r: AHT.Universal(r[0]))

T_LITERAL = ((Token(r'"""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""', group=0, as=eval)
             |Token(r'"[^"\\]*(?:\\.[^"\\]*)*"', group=0, as=eval)) + IGN
          +  ((Omit(RawToken('@')) + IGN + T_LANGCODE)
             |(Omit(RawToken('^^')) + IGN + T_SYMBOL)
             |Default(None))
) >> AHT.Literal

T_NUMERIC_LITERAL = Token(r'[-+]?[0-9]+(\.[0-9]+)?(e[-+]?[0-9]+)?', group=0, as=eval)
T_THIS_NODE = RawToken('@this', as=AHT.ThisNode)
T_VARIABLE = Token('\?((?=\w)[^\d]\w*)', group=1, as=AHT.Variable)

T_NODE = T_LITERAL | T_NUMERIC_LITERAL | T_SYMBOL | T_VARIABLE | T_THIS_NODE | Defer(lambda: T_PATH_LIST) | Defer(lambda: T_PROPERTY_LIST_NODE) | Defer(lambda: T_FORMULA)

T_PATH = TokenSeries(T_NODE, skip=IGN, delimiter=(RawToken('!') | RawToken('^')), includeDelimiter=True, min=1, as=AHT.Path)
T_PATH_LIST = (Omit(RawToken('(')) + TokenSeries(T_PATH, skip=IGN) + Omit(RawToken(')'))) >> (lambda r: AHT.PathListNode(r[0]))

T_VERB = (RawToken('<=', as=AHT.ImpliedBy)
         |RawToken('=>', as=AHT.Implies)
         |RawToken('=', as=AHT.SameAs)
         |RawToken('a', as=AHT.IsA)
         |((Omit(RawToken('has')) + IGN + T_PATH) >> (lambda r: r[0]))
         |((Omit(RawToken('is')) + IGN + T_PATH + IGN + Omit(RawToken('of'))) >> (lambda r: AHT.PassiveVerb(r[0])))
		 |T_PATH
)

T_PROPERTY_LIST = TokenSeries((T_VERB + TokenSeries(T_PATH, skip=IGN, delimiter=RawToken(','))), delimiter=RawToken(';'), skip=IGN)
T_PROPERTY_LIST_NODE = (Omit(RawToken('[')) + IGN + (T_PROPERTY_LIST ^ 'Expected property list') + IGN + Omit(RawToken(']'))) >> (lambda r: AHT.PropertyListNode(r[0]))
T_SIMPLE_STATEMENT = (T_PATH + IGN + (T_PROPERTY_LIST ^ 'Expected property list')) >> AHT.SimpleStatement
T_STATEMENT = T_SIMPLE_STATEMENT | T_EXISTENTIAL | T_UNIVERSAL | T_PREFIX_DECLARATION | T_KEYWORDS_DECLARATION 
T_STATEMENT_LIST = (TokenSeries(T_STATEMENT, delimiter=RawToken('.'), skip=IGN) + Skip(RawToken('.'))) >> (lambda r: AHT.StatementList(r[0]))
T_FORMULA = (Omit(RawToken('{')) + (T_STATEMENT_LIST ^ 'Expected statements') + Omit(RawToken('}') ^ 'Expected }')) >> (lambda r: AHT.Formula(r[0]))
T_DOCUMENT = (IGN + T_STATEMENT_LIST + IGN + (EOF ^ 'Expected end of input')) >> (lambda r: r[0])

def parse(string):
	return ZestyParser(string).scan(T_DOCUMENT)

if __name__ == '__main__':
	print parse(sys.stdin.read())