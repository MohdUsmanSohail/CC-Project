from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.icg import IRGenerator,IRPretty
from src.optimization import ConstantFolder,DeadCodeEliminator

class Backend:
    def __init__(self,source_code: str, verbose: bool = False):
        self.source_code = source_code
        self.verbose = verbose

        self.tokens = []
        self.ast = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.ir_instructions = []

    def run(self):
        lexer = Lexer(self.source_code)
        self.tokens = lexer.tokenize()
        if self.verbose:
            print("Tokens: ")
            for tok in self.tokens:
                print(tok)

        parser = Parser(self.tokens)
        self.ast = parser.parse()
        if self.verbose:
            print("\nAST: ")
            print(self.ast)

        self.semantic_analyzer.analyze(self.ast)
        if self.verbose:
            print("\nSemantic analysis passed.")
        
        ir_gen = IRGenerator()
        self.ir_instructions = ir_gen.generate(self.ast)
        if self.verbose:
            print("\nInitial IR: ")
            IRPretty(self.ir_instructions).pretty()

        const_folder = ConstantFolder(self.ir_instructions)
        self.ir_instructions = const_folder.fold()
        if self.verbose:
            print("\nAfter constant folding: ")
            IRPretty(self.ir_instructions).pretty()

        dce = DeadCodeEliminator(self.ir_instructions)
        self.ir_instructions = dce.eliminate()
        if self.verbose:
            print("\nAfter dead code elimination, Raw IR objects: ")
            for instr in self.ir_instructions:
                print(repr(instr))
            # IRPretty(self.ir_instructions).pretty()

        return self.ir_instructions