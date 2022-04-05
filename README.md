Tiny
====

This is an attempt to create a[ Tiny BASIC compiler](https://en.wikipedia.org/wiki/Tiny_BASIC). 
This project is entirely inspired by the series of articles published by Austin Henley an building a compiler that you can find [here](https://austinhenley.com/blog/teenytinycompiler1.html).

In its current, it only supports the syntax specification that can be found in the `grammar.txt` file in the project dir.


The only dependency this project has is the google yapf formatter tool.
 To use it, enable a python virtual environment (if that is still a thing whenever you are reading this)
 then install yapf with pip (if that still exists) then run the tool with the `-i` flag to enable in-place formatting.

NOTE: This project does not use the yapf tool anywhere in the code, it is to be used explicitly as a CLI tool like clang-format. 
