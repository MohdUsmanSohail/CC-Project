import argparse
import sys
from src.codegen import Backend,Executor

def run_file(path,verbose=False):
    try:
        with open(path,"r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        return
    
    backend = Backend(source,verbose=verbose)
    ir = backend.run()

    executor = Executor(ir,verbose=verbose)
    executor.run()

def repl(verbose=False):
    print("DataFlow Interactive Mode")
    print("Type code and press Enter. Type ':quit' to exit.\n")

    buffer = []

    while True:
        line = input(">>> ")
        if line.strip() == ":quit":
            break

        if line.strip() == "":
            #Empty line means run accumulated code
            source = "\n".join(buffer)
            buffer.clear()

            backend = Backend(source,verbose=verbose)
            ir = backend.run()

            executor = Executor(ir,verbose=verbose)
            executor.run()
            print()
        else:
            buffer.append(line)

def main():
    parser = argparse.ArgumentParser(description="DataFlow compiler and interpreter")
    parser.add_argument("file",nargs="?",help="Input source file (.dsl)")
    parser.add_argument("-v","--verbose",action="store_true",help="Show compiler internals")
    parser.add_argument("-i","--interactive",action="store_true",help="Start interactive REPL")

    args = parser.parse_args()

    if args.interactive:
        repl(verbose=args.verbose)
    elif args.file:
        run_file(args.file,verbose=args.verbose)
    else:
        print("No input file provided. Use -i for interactive mode.")
        parser.print_help()

if __name__ == "__main__":
    main()