# Pregunta 5

# SELECT * FROM noticias WHERE bag_of_words ? 'keyword';

from enum import Enum, auto
import pandas as pd
import warnings
import nltk
from abc import ABC, abstractmethod
import spacy

warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

nlp = spacy.load("es_core_news_sm")

stemmer = nltk.SnowballStemmer("spanish")

# method = "stemming"
method = "lemmatization"

class Token():
    class Type():
        (
            TERM, AND, OR, ANDNOT, LPAR, RPAR, END, ERR
        ) = range(8)
    token_names = ["TERM", "AND", "OR", "ANDNOT", "LPAR", "RPAR", "END", "ERR"]
    def __init__(self, type : Type, lexema : str = ""):
        self.type = type
        self.lexema = lexema

    def __str__(self):
        if self.lexema:
            return f"{Token.token_names[self.type]}({self.lexema})"
        else:
            return Token.token_names[self.type]
        
class Scanner():
    def __init__(self, input : str):
        self.input = input + "\0"
        self.first = 0
        self.current = 0

    def start_lexema(self) -> None:
        self.first = self.current

    def get_lexema(self) -> str:
        return self.input[self.first:self.current]
    
    def next_token(self) -> Token:
        self.start_lexema()
        c = self.input[self.current]
        state = 0
        while True:
            if state == 0:
                if c.isspace():
                    self.current += 1
                    c = self.input[self.current]
                    self.start_lexema()
                    state = 0
                elif c == '(':
                    self.current += 1
                    c = self.input[self.current]
                    return Token(Token.Type.LPAR)
                elif c == ')':
                    self.current += 1
                    c = self.input[self.current]
                    return Token(Token.Type.RPAR)
                elif c == '\0':
                    return Token(Token.Type.END)
                else:
                    state = 1
            elif state == 1:
                if not c.isspace() and c not in ['\0', '(', ')']:
                    self.current += 1
                    c = self.input[self.current]
                    state = 1
                else:
                    state = 2
            elif state == 2:
                lexema = self.get_lexema()
                if lexema == "AND":
                    return Token(Token.Type.AND)
                elif lexema == "OR":
                    return Token(Token.Type.OR)
                elif lexema == "AND-NOT":
                    return Token(Token.Type.ANDNOT)
                else:
                    return Token(Token.Type.TERM, lexema)

class Op(Enum):
    AND = auto()
    OR = auto()
    ANDNOT = auto()
    
class Query():
    def __init__(self):
        self.expression : Expression = None

    def get_sql_query(self) -> str:
        if not self.expression:
            raise Exception("Invalid Query")
        
        return f"SELECT * FROM noticias WHERE {self.expression.get_sql_query()}"

class Expression(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get_sql_query(self):
        pass

class BinaryExpression(Expression):
    def __init__(self, left : Expression, op : Op, right : Expression):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def get_sql_query(self):
        op = ""

        match self.op:
            case Op.AND:
                op = "AND"
            case Op.OR:
                op = "OR"
            case Op.ANDNOT:
                op = "AND NOT"

        return f"{self.left.get_sql_query()} {op} {self.right.get_sql_query()}"

class TermExpression(Expression):
    def __init__(self, term : str):
        super().__init__()
        self.term = term

    def get_sql_query(self):
        if method == "stemming":
            return f"bag_of_words ? '{stemmer.stem(self.term)}'"
        elif method == "lemmatization":
            return f"bag_of_words ? '{nlp(self.term)[0].lemma_}'"
        else:
            raise Exception("Unknown method")

class ParenthesisExpression(Expression):
    def __init__(self, exp : Expression):
        super().__init__()
        self.exp = exp

    def get_sql_query(self):
        return f"({self.exp.get_sql_query()})"

class ParseError(Exception):
    def __init__(self, error : str):
        self.error = f"Parse error: {error}"
        super().__init__(self.error)

class Parser():
    def __init__(self, scanner : Scanner):
        self.scanner = scanner
        self.current : Token = None
        self.previous : Token = None

    def parse_error(self, error : str):
        raise ParseError(error)

    def match(self, type : Token.Type) -> bool:
        if self.check(type):
            self.advance()
            return True
        else:
            return False

    def check(self, type : Token.Type) -> bool:
        if self.is_at_end():
            return False
        else:
            return self.current.type == type

    def advance(self) -> None:
        if not self.is_at_end():
            temp = self.current
            self.current = self.scanner.next_token()
            self.previous = temp
            if self.check(Token.Type.ERR):
                self.parse_error(f"unrecognized character: {self.current.lexema}")

    def is_at_end(self) -> bool:
        return self.current.type == Token.Type.END
    
    def parse(self) -> Query:
        try:
            self.current = self.scanner.next_token()
            return self.parse_query()
        except ParseError as e:
            print(e.error)
            return Query()

    def parse_query(self) -> Query:
        query = Query()
        query.expression = self.parse_or()
        return query

    def parse_or(self) -> Expression:
        exp = self.parse_and()
        while self.match(Token.Type.OR):
            right = self.parse_and()
            exp = BinaryExpression(exp, Op.OR, right)
        return exp

    def parse_and(self) -> Expression:
        exp = self.parse_and_not()
        while self.match(Token.Type.AND):
            right = self.parse_and_not()
            exp = BinaryExpression(exp, Op.AND, right)
        return exp
    
    def parse_and_not(self) -> Expression:
        exp = self.parse_term()
        while self.match(Token.Type.ANDNOT):
            right = self.parse_term()
            exp = BinaryExpression(exp, Op.ANDNOT, right)
        return exp
    
    def parse_term(self) -> Expression:
        if self.match(Token.Type.TERM):
            return TermExpression(self.previous.lexema)
        elif self.match(Token.Type.LPAR):
            exp = ParenthesisExpression(self.parse_or())
            if not self.match(Token.Type.RPAR):
                self.parse_error("expected ')'")
            return exp
        else:
            self.parse_error("expected term or '('")

def test_scanner(scanner : Scanner) -> None:
    while True:
        token = scanner.next_token()
        print(token)
        if token.type == Token.Type.END:
            break
        if token.type == Token.Type.ERR:
            print("Scanner error: unknown token")
            break

def create_sql_query(query):
    scanner = Scanner(query)
    parser = Parser(scanner)
    return parser.parse().get_sql_query()

def apply_boolean_query(query, db_connection):
    try:
        sql_query = create_sql_query(query)

        print(f"Ejecutando consulta sql: {sql_query}")

        df = pd.read_sql(sql_query, db_connection)
        return df
    except:
        return pd.DataFrame()

def test(db_connection):
    test_queries = [
        "transformación AND sostenible OR startup",
        "(México OR Perú) AND-NOT (China OR Chile)",
        "inflación OR recesión OR desempleo",
        "guerra OR paz AND europa",
        "salud AND pandemia OR vacuna",
        "(educación OR ciencia) AND gobierno",
        "(amazon AND google) OR (microsoft AND apple) AND facebook",
        "((apple AND iphone) OR (samsung AND android)) AND-NOT huawei"
    ]

    for query in test_queries:
        print(f"Probando consulta: '{query}'")
        results = apply_boolean_query(query, db_connection)

        if results.empty:
            print("No se encontraron documentos.")
        else:
            print("Resultados encontrados:")
            print(results[['id', 'contenido']].head())
        print("-" * 50)
        print()
    db_connection.close()

if __name__ == "__main__":
    query = "((educación OR ciencia) AND gobierno) OR ((México OR Perú) AND-NOT (China OR Chile)) OR (transformación AND sostenible OR startup)"
    print(create_sql_query(query))