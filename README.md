# DataFlow: A mini language for table manipulation and lightweight analytics

  A compact DSL inspired by SQL + Python list comprehensions, designed for:

  - Loading data tables
  - Filtering
  - Mapping/transformations
  - Simple aggregations
  - Printing results

  # What is in this repository

    - src: The source code folder. Contains all relevant files for AST generation, lexing, parsing, semantic analysis, intermediate code generation, code optimization, and running executable code.
    - employees.csv: A lightweight table containing employee records, for demonstration purposes.
    - Test files: Namely: program.dsl (works completely and demonstrates use of all the different keywords in our grammar); parsing_fail.dsl (to show the parser in action); semantic_fail.dsl (to show semantic  analysis in action)
    - Handwritten artifacts: For lexical analysis, syntax analysis, and semantic analysis

  # How to run

    DataFlow programs can be run from the command line in one of two modes: file mode and interactive mode.
    File mode: Write your code and save is as file_name.dsl. Then on the command line, run: "python -m src.main file_name.dsl"
    Use the --verbose flag to show compiler internals
    Interactive mode: On the command line, run "python -m src.main -i" for interactive mode.
    You will be prompted to add your code line-by-line. Leave an empty line to run the accumulated code. Type ":quit" to exit interactive mode.
