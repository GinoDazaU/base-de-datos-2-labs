# Pregunta 5

# SELECT * FROM noticias WHERE bag_of_words ? 'keyword';

from enum import Enum, auto
import pandas as pd

class Token():
    class Type():
        (
            TERM, OP, END, ERR
        ) = range(4)
    token_names = ["TERM", "OP", "END", "ERR"]
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
                elif c == '\0':
                    return Token(Token.Type.END)
                else:
                    state = 1
            elif state == 1:
                if not c.isspace() and c != '\0':
                    self.current += 1
                    c = self.input[self.current]
                    state = 1
                else:
                    state = 2
            elif state == 2:
                lexema = self.get_lexema()
                if lexema in ["AND", "OR", "AND-NOT"]:
                    return Token(Token.Type.OP, lexema)
                else:
                    return Token(Token.Type.TERM, lexema)

class Op(Enum):
    AND = auto()
    OR = auto()
    ANDNOT = auto()
    
class Query():
    def __init__(self):
        self.left : str = None
        self.op : Op = None
        self.right : str = None

    def get_sql_query(self) -> str:
        op = ""
        if not self.op or not self.left or not self.right:
            raise Exception("Invalid Query")
        match self.op:
            case Op.AND:
                op = "AND"
            case Op.OR:
                op = "OR"
            case Op.ANDNOT:
                op = "AND NOT"
        sql_query = f"SELECT * FROM noticias WHERE bag_of_words ? '{self.left}' {op} bag_of_words ? '{self.right}'"
        return sql_query

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
        if not self.match(Token.Type.TERM):
            self.parse_error("expected a term at the start of the query")
        query.left = self.previous.lexema
        if not self.match(Token.Type.OP):
            self.parse_error("expected an operation after the term")
        match self.previous.lexema:
            case "AND":
                query.op = Op.AND
            case "OR":
                query.op = Op.OR
            case "AND-NOT":
                query.op = Op.ANDNOT
            case _:
                self.parse_error("unknown operation")
        if not self.match(Token.Type.TERM):
            self.parse_error("expected a term after the opreation")
        query.right = self.previous.lexema
        if not self.current.type == Token.Type.END:
            self.parse_error("unexpected items after query")
        return query

def test_scanner(scanner : Scanner) -> None:
    while True:
        token = scanner.next_token()
        print(token)
        if token.type == Token.Type.END:
            break
        if token.type == Token.Type.ERR:
            print("Scanner error: unknown token")
            break

def apply_boolean_query(query, db_connection):
    try:
        scanner = Scanner(query)
        parser = Parser(scanner)

        parsed = parser.parse()

        sql_query = parsed.get_sql_query()

        print(sql_query)

        df = pd.read_sql(sql_query, db_connection)
        return df
    except:
        return pd.DataFrame()

def test(db_connection):
    test_queries = [
        "transformación AND sostenible", # Consulta con AND
        "México OR Perú",  # Consulta con OR
        "México AND-NOT Perú",  # Consulta con AND-NOT
        "nonexistent term",  # no debería devolver resultados
    ]

    for query in test_queries:
        print(f"Probando consulta: '{query}'")
        results = apply_boolean_query(query, db_connection)

        if results.empty:
            print("No se encontraron documentos.")
        else:
            print("Resultados encontrados:")
            print(results[['id', 'text_column']].head())
        print("-" * 50)
    db_connection.close()