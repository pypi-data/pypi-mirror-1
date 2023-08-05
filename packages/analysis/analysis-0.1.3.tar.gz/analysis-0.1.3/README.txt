Introduction
------------

The analysis package provides support for the analysis of Python source code
beyond that provided by the compiler standard library package. When performing
an analysis of a Python module, the software first obtains the abstract syntax
tree using the compiler package; then it annotates the nodes in that package
with information it has deduced from the anticipated behaviour of the program.

Additional modules are provided for code generation, and although these
modules are as yet incomplete, they do provide an insight into the conclusions
drawn in the analysis activity.

Quick Start
-----------

First, check the dependencies below. The test suite produces C programs which
require libgc in order to build and run.

Try running the test suite:

PYTHONPATH=. python tools/compile.py

To preserve the compiled programs, try the following:

PYTHONPATH=. python tools/compile.py --preserve

Try running the simple code generator to get code listings in various
languages (but only C is actively supported at the moment):

python dump.py tests/fib.py --C

(This overwrites the special built-in declarations in tools/C/builtins.h.)

Try running the test program in interactive mode and examining the module
object 'm' with the 'ldir', 'lref' and 'ltype' functions:

python -i test.py tests/class.py

>>> ldir(m)
[['C', 'B']]
>>> ldir(m, "B")
[['x', '__init__']]
>>> lref(m, "B.x")
[AssAttr(Name('self'), 'x', 'OP_ASSIGN'), AssAttr(Name('self'), 'x',
'OP_ASSIGN'), AssAttr(Getattr(Name('C'), 'b1'), 'x', 'OP_ASSIGN')]
>>> lref(m, "B.x")[0]
AssAttr(Name('self'), 'x', 'OP_ASSIGN')
>>> ltype(lref(m, "B.x")[0])

Documentation about aspects of the package's design and implementation can be
found in the docs directory, with the most useful document being docs/AST.html
- a reference covering the annotation attributes added to abstract syntax tree
nodes during the analysis activity.

Contact, Copyright and Licence Information
------------------------------------------

No Web page has yet been made available for this work, but the author can be
contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Other works included in this distribution include cexcept.h - see
docs/README-cexcept.txt for that software's copyright and licence information.

Dependencies
------------

libgc       Also known as the Boehm-Demers-Weiser conservative garbage
            collector. Tested with version 6.3 (packages libgc1 6.3-1 and
            libgc-dev 6.3-1 on Ubuntu/Kubuntu).

New in analysis 0.1.3 (Changes since analysis 0.1.2)
----------------------------------------------------

  * Added missing dependency documentation.
  * Fixed return value recording so that multiple internal functions (such as
    those investigated in operator nodes) provide all known return values
    (rather than just the last specialisation's return values, as was the
    case).
  * Fixed specialisation tracking so that exceptions in specialisation
    processing do not confuse the processor.
  * Fixed method object comparisons in the C source code generation.
  * Replaced the usage of nodes as internal function arguments with
    references, adding special refcontexts to generate appropriate code; this
    affected AssTuple, For, Slice, Subscript.

New in analysis 0.1.2 (Changes since analysis 0.1.1)
----------------------------------------------------

  * Changed the generated C source code for sequences of function calls,
    creating an additional runtime function to make it work.
  * Added better detection and generation of class attribute access via
    references (ie. the self object).
  * Added usage of exceptions (using the cexcept project's code).
  * Introduced "for" loops and StopIteration exceptions.
  * Removed _tmp, _expr, _iter and _stream from the generated C source code
    and runtime, definitively replacing them with usage of the expression
    stack, which has been implemented using local variables.

New in analysis 0.1.1 (Changes since analysis 0.1)
--------------------------------------------------

  * Made many improvements to C source code generation in order to allow most
    of the test programs to be translated, compiled and run. This includes a
    preliminary runtime library which will either need more attention later
    on or be replaced by something better.
  * Added annotations to support name generation, notably _name_context and
    wider usage of _qualified_name.
  * Improved/fixed specialisation naming so that specialisations do not
    conflict with each other.
  * Added "native" method annotations so that the built-in functions and
    methods (or at least their method object "handles") can be generated where
    appropriate.
  * Various redundant modules have been removed.
  * The tools/6502 directory has been removed until further notice.

Notes for analysis 0.1
----------------------

  * The tools/6502 directory is not included in this release since it includes
    and/or depends upon tools which are not suitably/explicitly licensed.

Future Work
-----------

Instantiation:
    Consider list.__str__ and list.__repr__:
        The overhead in listing the contents of lists could be considerable
        especially where many different types are put in lists.

Instantiation and specialisation ("data polymorphism"):
    Loss of precision in function signatures/specialisations might need to be
    overcome using an improved scheme for instantiating/identifying
    objects/references during analysis and/or determining suitable signatures
    for specialisations. The docs directory contains some discussion documents
    on this topic.

Code generation:
    The code generation for the C programming language should be improved.
    Assembly language generation could also be done, although developing
    suitable runtime libraries is time consuming.

Release Procedures
------------------

Update the analysis/__init__.py __version__ attribute.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the release information in the PKG-INFO file.
Tag, export.
Archive, upload.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Generating the API Documentation
--------------------------------

In order to prepare the API documentation, it is necessary to generate some
Web pages from the Python source code. For this, the epydoc application must
be available on your system. Then, inside the distribution directory, run the
apidocs.sh tool script as follows:

./tools/apidocs.sh

Some warnings may be generated by the script, but the result should be a new
apidocs directory within the distribution directory.
