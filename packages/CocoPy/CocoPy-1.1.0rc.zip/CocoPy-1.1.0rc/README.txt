!!!PLEASE NOTE!!!
This distribution is a release candidate.

Setup and usage information can be found in section 3 of
documentation/CocoDoc.htm.  CocoDoc.htm contains everything you need to
use Coco for Python.

This file contains a list of the contents of the distribution and a
development roadmap.


CONTENTS OF THIS DISTRIBUTION

This distribution of Coco includes the following:

   Coco root directory

      The application files

      Coco.py            - The main application file
      Scanner.py         - The lexical analizer for attributed grammars
      Parser.py          - The parser for attributed grammars

      DriverGen.py       - Generates the main application
      ParserGen.py       - Generates the parser
      CodeGenerator.py   - Common code generation routines
      CharClass.py       - Implementation of character classes
      Errors.py          - Tracking and reporting errors in the source grammar
      Trace.py           - Routines for generating trace files
      Core.py            - Scanner generator and various support classes.

      Other

      setup.py           - Python distribution utilities setup script for Coco.
      setupInfo.py       - CocoPy Version information
      README.txt         - this file.

   /documentation
      
      license.txt        - The license agreement
      CocoDoc.htm        - The documentation for CocoPy
      howToBootstrap.txt - Instructions on how to bootstrap Coco (outdated)
      DataStructurres.pdf- A description of the workings of Coco
      pimaker.txt        - Documentation of pimaker.

   /examples

      Various example Attributed Grammars, not all are LL(1).

   /frames

      The basic Frame files.  These are template files used by the code
      generation routines.

   /sources

      These are the source files needed to bootstrap CocoPy.

      Coco.atg       - The grammar for the Coco language.
      Coco.frame     - Frame file for Coco's main module.
      Parser.frame   - Frame file for Coco's parser module.
      Scanner.frame  - Frame file for Coco's scanner module.

   /pimaker (Python Interactive Make utility)

      The Python Interactive Make utility written in Coco as a practical
      example of Coco usage.

      pimaker.atg    - The grammar for a makepi.how file.
      pimaker.frame  - The frame file for pimaker's main module.
      pimakerlib.py  - Library of routines needed by pimaker.
      makepi.how     - Pimaker's equivalent to a 'makefile' to bootstrap Coco.

   /testSuite

      The testbootstrap target in pimaker simply diffs the generated files
      coco.py, Parser.py and Scanner.py.  If there are no differences,
      the test passes.  However, when modifications are made to Coco.py
      this sort of testing is not sufficient.
      
      The suite of tests is in this directory are ported for the C#
      implementation of Coco/R.  They test Coco/R features.  To run the
      test suite open a command shell into the testSuite folder and execute
      the following:
      
         >>> python cocopTester.py


ROADMAP

   - Version numbering is tentative.


Release#   Goal
--------   ------------------------------------------------------
1.0.10b2.  Coco now bootstraps correctly.

1.1.0rc.   *** Release Candidate -- Coco now successfully runs the test suite
           from the C# implementation.

1.1.1rc.   Coco now correctly parses the examples and reports all the errors
           in the example grammars.

1.1.2rc.   Code generated from examples now sucessfully loads into python
           using 'python name.py'

1.1.3rc    Code generated from examples now successfully parses input
           and generates errors when appropriate.

1.2.0.     *** Final -- No bugs reported or found for some (as yet
           undetermined) period of time (e.g. 3 months).

1.2.x.     Various bug fix releases

1.3.0.     Coco is now updated to equivalence of the latest Java & C#
           implementations.

2.0.0.     *** Enhancements -- Incorporated various enhancements
           - get rid of all the static code
           - Improve indentation of generated code (currently much is
             hardcoded).  Should be more flexible to user's preference.


As I move Coco towards a final release I also want to continuously update
and refine the documentation.

