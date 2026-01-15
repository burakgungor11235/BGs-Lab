+++
title = "Arith"
description = "A complete command-line arithmetic interpreter built from the ground up in Rust. Features a multi-stage pipeline: lexer, Pratt parser, and a stack-based VM."
date = 2025-08-25
template = "project-single.html"
[extra]
stack = ["Rust", "Compiler Design", "VM"]
link = "https://github.com/TheBruh141/arith"
+++

Arith is a deep dive into compiler design, implementing a full interpretation pipeline from lexical analysis and parsing to bytecode compilation and execution on a custom stack-based virtual machine.

### Architectural Achievements
- **Hand-written Lexer & Pratt Parser**: Built from first principles to construct a robust Abstract Syntax Tree (AST).
- **Two-Phase Execution Engine**: lowered the AST into a custom bytecode instruction set (IR) for performance, exceeding the capabilities of simple tree-walking interpreters.
- **Bytecode & VM**: A stack-based virtual machine (VM) executes the compiled instructions, demonstrating a sophisticated understanding of language implementation.
- **Precise Error Handling**: A multi-layered system provides user-friendly feedback with exact line and column numbers.

Built with **Rust** for high performance and memory safety.
