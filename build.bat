@echo off

python src\tiny.py %1

clang-format -i --style=llvm test\*.c
