Introduction
------------

The analysis package provides support for the analysis of Python source code
beyond that provided by the compiler standard library package. When performing
an analysis of a Python module, the software first obtains the abstract syntax
tree using the compiler package; then it annotates the nodes from that package
with information it has deduced from the anticipated behaviour of the program.

Additional modules are provided for code generation, and although these
modules are as yet incomplete, they do provide an insight into the conclusions
drawn in the analysis activity. Modules are also provided for the production
of visual summaries showing the analysis activity's conclusions, and these
summaries can be viewed in a suitably up-to-date Web browser.

Viewing Analysis Results
------------------------

First, check the Web browser support below. The documentation suite produces
HTML documents which use CSS features that are not well supported in all
browsers.

Try running the summary/documentation suite:

PYTHONPATH=. python tools/docgen.py

This produces directories of HTML files alongside each Python program in the
tests directory. An index document can be generated as follows:

python tools/make_docgen_index.py tests

This produces an analysis-summaries.html file in the current directory.

Testing Program Compilation
---------------------------

First, check the dependencies below. The test suite produces C programs which
require libgc in order to build and run.

Try running the test suite:

PYTHONPATH=. python tools/compile.py

This produces directories of C source files alongside each Python program in
the tests directory. Each program is executed and should result in either
"SUCCEEDED" or "FAILED" being displayed depending on whether the generated
programs produce identical results to the original Python programs.

NOTE: Some of the programs do not produce the correct results. See the notes
NOTE: below on deficiencies for some reasons for this.

Testing Individual Program Compilation
--------------------------------------

Try running the simple code generator to get code listings in various
languages (but only C and HTML are supported at the moment):

python dump.py tests/fib.py --CC fib-sources

This is similar to doing the following...

PYTHONPATH=. python tools/compile.py --only tests/fib.py

...but with the generated code written to the tests/fib-sources directory.
If the --only switch is omitted, the generated program is executed and the
results compared with the original Python program (as described above).

Testing Individual Summary Generation
-------------------------------------

Try running the simple code generator to get summary information:

python dump.py tests/fib.py --HTML fib-files

This is similar to doing the following...

PYTHONPATH=. python tools/docgen.py tests/fib.py

...but with the generated documents written to the tests/fib-files directory.

Interactive Analysis
--------------------

Try running the test program in interactive mode and examining the module
object 'm' with the 'ldir', 'lref' and 'ltype' functions:

python -i test.py tests/class.py

>>> ldir(m)
[['C', 'B']]
>>> ldir(m, "B")
[['__init__']]
>>> ldir(m, "C")
[['x', 'b1', 'b2']]
>>> lref(m, "C.x")
[AssName('x', 'OP_ASSIGN'), AssAttr(Name('C'), 'x', 'OP_ASSIGN')]
>>> lref(m, "C.x")[0]
AssName('x', 'OP_ASSIGN')
>>> lname(ltype(lref(m, "C.x")[0]))
'int'

Documentation about aspects of the package's design and implementation can be
found in the docs directory, with the most useful document being docs/AST.html
- a reference covering the annotation attributes added to abstract syntax tree
nodes during the analysis activity.

Contact, Copyright and Licence Information
------------------------------------------

The Web page for this work can be found at the following location:

http://www.boddie.org.uk/python/analysis.html

The author can be contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Other works included in this distribution include cexcept.h - see
docs/README-cexcept.txt for that software's copyright and licence information.

Dependencies for the Test Suite (C Program Generation)
------------------------------------------------------

libgc       Also known as the Boehm-Demers-Weiser conservative garbage
            collector: http://www.hpl.hp.com/personal/Hans_Boehm/gc/
            Tested with version 6.3 (packages libgc1 6.3-1 and libgc-dev 6.3-1
            on Ubuntu/Kubuntu).

Web Browser Support for the Documentation Suite Output
------------------------------------------------------

The documentation suite uses CSS 2 features to display pop-up information
about nodes in program syntax trees. Here is a overview of browsers tested
with the suite's output:

Konqueror   Recommended:
            Tested with 3.4.0 (from KDE 3.4.0). The pop-up information appears
            correctly.
Opera       Recommended with reservations:
            Tested with 8.51 on Kubuntu Hoary. Whilst the pop-up information
            appears, it is not erased correctly.
Firefox     Not recommended:
            Tested with 1.0.7 on Kubuntu Hoary. The pop-up information does
            not appear at all.

New in analysis 0.1.7 (Changes since analysis 0.1.6)
----------------------------------------------------

  * Introduced undefined values in the processing of conditional blocks. Such
    values admit the possibility that certain names may not be defined at
    run-time and may therefore need additional testing in generated programs.
  * Introduced "undesirable" values which are recorded so that code generators
    may be aware that some operations may not be defined and should cause an
    error under the appropriate conditions at run-time.
  * Overhauled the C output generation, introducing an output generator.
  * Improved optimised value propagation and C output generation, changing and
    simplifying various generated code details to improve performance.
  * Changed the production of qualified names in analysis.namespace.
  * Moved builtins.py into a special lib directory accessible to programs
    under analysis.
  * Rewrote various built-in types in Python, removing certain functions and
    structures from the C runtime library.
  * Changed the naming scheme for the builtins module and the associated
    runtime library.
  * Added better argument/parameter matching.
  * Added augmented assignment support.
  * Added short-circuiting to the HTML output generation.
  * Fixed analysis.utils.prompt.
  * Introduced the concept of "special" names in order to deal with classes
    inside functions: special names are like globals but are not associated
    with the module namespace.
  * Changed the tools to use CMDsyntax-based options.
  * Moved the definition of special names (True, False, None, Undefined) to
    the AnalysisSession object.
  * Fixed blockage handling, ensuring that blockages cause propagation back
    to the blocking specialisation.
  * Changed the _specialisation annotation to _specialises, providing a
    reference to the specialised function - useful for looking up the argument
    details on subsequent occasions.
  * Added filtering of locals according to the operations performed on them,
    along with the raising of exceptions or the usage of default values when
    undesirable (or filtered-out) types are detected at run-time.
  * Removed cpu6502 generator and instruction visitor.

New in analysis 0.1.6 (Changes since analysis 0.1.5)
----------------------------------------------------

  * Introduced the AnalysisSession class to manage the processing of
    potentially many files.
  * Added the _inherited annotation and introduced superclass attribute
    initialisation for subclasses in the generated C source code.
  * Changed the HTML summary generation to produce directories of HTML files,
    each containing a summary of a module involved in a particular program.
  * Changed the C program generation to produce directories of C source files
    with separate header files suitable for inclusion.

New in analysis 0.1.5 (Changes since analysis 0.1.4)
----------------------------------------------------

  * Simplified the _targets annotations, using specially created nodes in the
    AST in places which previously justified the use of complicated _targets
    annotations.
  * Added HTML summary generation, showing the programs as Web pages with
    pop-up information about the types and targets of nodes.
  * Added some support for imports (moving various analysis.utils functions
    into analysis.source).
  * Updated the FSF contact address.

New in analysis 0.1.4 (Changes since analysis 0.1.3)
----------------------------------------------------

  * Improved the comparison methods and added special built-in functions
    providing run-time support for the "is", "is not" and "not" operators,
    along with improved analysis support for those operators.
  * Introduced proper logical operator support using __true__ methods which
    return a boolean value according to the state of the object concerned.
  * Added logical operator support in the generated C source code, attempting
    to replicate Python language behaviour ("a and b" returns b or False, for
    example).

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

Deficiencies
------------

The generated C program code does not necessarily emulate the original Python
program behaviour for a number of reasons:

  * Inherited attributes are given a "name context" which states how they can
    be obtained. Since Python permits instance attributes to override class
    attributes, any situations where an attribute is in one case accessed via
    a class, then in another case accessed via an instance, will cause a name
    context to be produced (for instance access) that is not always suitable.

  * Instance type testing does not function correctly where such tests need
    to be done at run-time. Since the generated C code does not record class
    hierarchy details, the runtime library test for instance types can only
    test for a specific type, rather than membership of a type hierarchy. This
    can be resolved by providing a list of types to test against as node
    annotations, but this is not yet done.

  * Full exception handling is not yet done. Consequently, the undefined name
    examples, which produce NameError exceptions, do not work correctly.

Future Work
-----------

Instantiation:

    Consider list.__str__ and list.__repr__:
        The overhead in listing the contents of lists could be considerable
        especially where many different types are put in lists.
        One way of alleviating the pollution of frequently-used types is to
        introduce subclasses which signal that the purpose of the subclasses
        is different to that of the superclass.
        See tests/assign_list_subclasses.py for an example of this "semantic
        typing".

Instantiation and specialisation ("data polymorphism"):

    By treating all instances of each type alike, a certain loss of precision
    in function signatures/specialisations might occur that could be overcome
    using an alternative scheme for instantiating/identifying
    objects/references during analysis and/or determining more precise
    signatures for specialisations. The docs directory contains some
    discussion documents on this topic.

Code generation:

    The code generation for the C programming language should be improved:
        Currently mixed "name contexts" are not supported, meaning that access
        to class attributes and instance attributes cannot happen in the same
        place.
        The generated code is currently inefficient due to the way it emulates
        a stack machine.
        Building lists is actually slower than CPython, which may be related
        to a number of things: inefficient code (see above), memory management
        issues such as inefficient allocation strategies...

    Assembly language generation could also be done, although developing
    suitable runtime libraries is time consuming:
        This has been abandoned for now.

Release Procedures
------------------

Update the analysis/__init__.py __version__ attribute.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the API documentation.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
Upload the example summaries.
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

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-analysis/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
