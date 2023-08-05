email -- a mail and MIME handling package
Copyright (C) 2001-2007 Python Software Foundation


Introduction

    The email package is a library for managing email messages, including MIME
    and other RFC 2822-based message documents.  It is intended to replace
    most of the functionality in several older standard modules such as
    rfc822, mimetools, multifile, mimify, and MIMEWriter, and other
    non-standard packages such as mimecntl.  It is compliant with most of the
    email related RFCs such as 2045-2047 (the MIME RFCs) and 2231.

    This version is identical to the package available in Python 2.5.  It is
    being made available as a standalone package for use in older Python
    releases.  A minimum of Python 2.3 is required.  Because the email package
    is part of Python, it is covered by the PSF license for Python, as
    described in the LICENSE.txt file.


Testing

    To test the email package, run the standard unit test suite from the
    directory that you unpacked the source in (i.e. the directory containing
    the setup.py file and this README file):

    % python testall.py

    You should see a couple of lines of dots followed by the number of tests
    ran and the time the tests took.  The test should end with an "OK".  If
    so, you're good to go.  Note that the exact number of tests depends on
    such things as whether you have the Japanese codecs installed or not.


Documentation and Examples

    The documentation, including the major changes in the package over time,
    can be found in the docs directory:

    docs/index.html

    If you're looking for examples, you might want to check out some
    of the tests.  There are a few examples in the documentation as
    well.


Installing

    To install simply execute the following at your shell prompt:

    % python setup.py install


Acknowledgements

    Here is a list of folks who have contributed code, examples, suggestions,
    bug reports, feedback, and encouragement:

    Anthony Baxter
    Martin Bless
    Oleg Broytmann
    Matthew Dixon Cowles
    Jeff Dairiki
    Quinn Dunkan
    Ben Gertzfield
    David Given
    Phil Hunt
    Tokio Kikuchi
    Sheila King
    Martin Koch
    Jason Mastaler
    Andrew McNamara
    Skip Montanaro
    Guido van Rossum
    Barry Warsaw
    Thomas Wouters

    Apologies to anybody I've left out (let me know!).


Contact Information

    The email-sig is the mailing list and community of users and developers of
    the package and related Python email technologies.  For more information:

    http://www.python.org/sigs/email-sig



Local Variables:
mode: indented-text
indent-tabs-mode: nil
End:
