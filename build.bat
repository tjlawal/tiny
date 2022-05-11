@echo off
set BUILD_DIR=output

python src\tiny.py %1

RD /S /Q %BUILD_DIR%
mkdir %BUILD_DIR%
move test\*.tiny.c output\
echo:
clang-format -i --style=llvm --Werror --verbose output\*.tiny.c
