Manual
++++++

Introduction
============

ConfigConvert provides a function to parse config files in the NestedRecord
format as well as a set of tools based on ConversionKit for handling common
config-handling tasks such as checking files and directories exist or importing
Python objects.

Converters
==========

To test the converters we'll need some imports:

.. sourcecode :: pycon

    >>> from conversionkit import Conversion

The ``existingDirectory()`` converter ensures the directory it recieves as input
exists and is not a file, otherwise it sets an error. If you run the tests that
accompany ConfigConvert from the ``test`` directory then the directory
``../test`` will exist but the directory ``../does_not_exist`` should not
exist. With this in mind here's a demonstration:

.. sourcecode :: pycon

    >>> from configconvert import existingDirectory
    >>>
    >>> Conversion('../test').perform(existingDirectory()).result
    '../test'
    >>> Conversion('../does_not_exist').perform(existingDirectory()).error
    "The directory doesn't exist"

The ``existingFile()`` converter is similar but checks for files:

.. sourcecode :: pycon

    >>> from configconvert import existingFile
    >>>
    >>> Conversion('doc.py').perform(existingFile()).result
    'doc.py'
    >>> Conversion('does_not_exist.py').perform(existingFile()).error
    "The file doesn't exist"

If you use the ``existingFile()`` converter on a directory or the
``existingDirectory()`` converter on a file you'll get an error:

.. sourcecode :: pycon

    >>> Conversion('doc.py').perform(existingDirectory()).error
    'The path is not a directory'
    >>> Conversion('../test').perform(existingFile()).error
    'The path is not a file'

Uniform Paths
-------------

Sometimes you'll want an absolute, normalised path returned from the converters
instead of the input value. You achieve this by setting ``uniform_path=True``:

.. sourcecode :: pycon

    >>> import os
    >>> path = Conversion('doc.py').perform(existingFile(uniform_path=True)).result
    >>> path == os.path.abspath(os.path.normpath(path))
    True
    >>> path = Conversion('../test').perform(existingDirectory(uniform_path=True)).result
    >>> path == os.path.abspath(os.path.normpath(path))
    True

Creating Files and Directories
------------------------------

Rather than setting an error if a file or directory is missing you might want
to create it. You can do this by setting ``try_to_create`` to ``True``. Let's 
set up a test directory:

.. sourcecode :: pycon

    >>> os.mkdir('test_data')

Now let's test the converters. First creating a file and adding some default content:

.. sourcecode :: pycon

    >>> os.path.exists('test_data/new_file.txt')
    False
    >>> file_content = u'Some data'
    >>> Conversion('test_data/new_file.txt').perform(
    ...     existingFile(
    ...         try_to_create = True,
    ...         file_content = file_content.encode('utf8'),
    ...     )
    ... ).result
    'test_data/new_file.txt'
    >>> os.path.exists('test_data/new_file.txt')
    True
    >>> fp = open('test_data/new_file.txt', 'rb')
    >>> fp.read().decode('utf8')
    u'Some data'
    >>> fp.close()

Handling a problem where the file cannot be created because the parent
directory doesn't exist:

.. sourcecode :: pycon

    >>> Conversion('does_not_exist/new_file.txt').perform(
    ...     existingFile(
    ...         try_to_create = True,
    ...         file_content = file_content.encode('utf8'),
    ...     )
    ... ).error
    "Could not create the file 'does_not_exist/new_file.txt'"

Raising an exception instead of creating an error:

.. sourcecode :: pycon

    >>> Conversion('does_not_exist/new_file.txt').perform(
    ...     existingFile(
    ...         try_to_create = True,
    ...         file_content = file_content.encode('utf8'),
    ...         raise_on_create_error = True,
    ...     )
    ... ).error
    Traceback (most recent call last):
      File ...
    IOError: [Errno 2] No such file or directory: 'does_not_exist/new_file.txt'

Now let's try the same thing with directories. First creating a directory if it
doesn't exist:

.. sourcecode :: pycon

    >>> os.path.exists('test_data/new_dir')
    False
    >>> Conversion('test_data/new_dir').perform(
    ...     existingDirectory(
    ...         try_to_create = True,
    ...     )
    ... ).result
    'test_data/new_dir'
    >>> os.path.exists('test_data/new_dir')
    True

Handling a problem where the directory cannot be created because the parent
directory doesn't exist:

.. sourcecode :: pycon

    >>> Conversion('does_not_exist/new_dir').perform(
    ...     existingDirectory(
    ...         try_to_create = True,
    ...     )
    ... ).error
    "Could not create the directory 'does_not_exist/new_dir'"

Raising an exception instead of creating an error:

.. sourcecode :: pycon

    >>> Conversion('does_not_exist/new_dir').perform(
    ...     existingDirectory(
    ...         try_to_create = True,
    ...         raise_on_create_error = True,
    ...     )
    ... ).error
    Traceback (most recent call last):
      File ...
    OSError: [Errno 2] No such file or directory: 'does_not_exist/new_dir'


Config Files
============

If you get used to working with the NestedRecord encoding it can be useful to also use it for config files.

There's an example config file in the ``test`` directory called ``test.conf``. It looks like this:

.. sourcecode :: pycon

    >>> fp = open('test.conf', 'rb')
    >>> contents = fp.read().decode('utf8')
    >>> fp.close()
    >>> print contents.strip()
    app.name = Application
    mail[0].name = James
    mail[0].address = james@example.com
    mail[1].name = Ian
    mail[1].address = ian@example.com
    app.description = This is a
        multiline
        description
    app.title = My App


The config file is made of options and values which are each defined on a
single line terminated by a \n character and separtated by only the three
characters `` = `` with exactly one space either side of the ``=`` sign. Any
extra spaces before the ``=`` are treated as an error and any extra spaces
afterwards are treated as leading spaces on the string. For example this:

::

    option =  value

would result in the option 'option' taking the value u' value'. Any extra
spaces after the option name are ignored though.

The parsed config file results in a dictionary with the options as ASCII
strings for the keys and the values as unicode strings for the values. The
options must start with the letters a-z, A-Z or _ and should contain only
letters, numbers or the _ character. Thus the option values have the same
naming rules as Python variables.

The file must use UNIX style line endings (ie each line ends in ``\n``) and
should normally be encoded as UTF-8. Values can therefore take any Unicode
character as long as the file is encoded correctly.

You can also specify multiline values. You do so by specifying the first line
of the multiline value on the same line as the option starting immediately
after the space after the equals sign (once again any extra spaces will be
treated as part of the value). All subsequent lines have to be indented 4
spaces. Any characters after those 4 spaces are treated as part of the line. In
fact the first line doesn’t have to contain any text if you are using a
multiline value, in which case the value will start with a ``\n`` character.
Here are two examples:

:: 

    option1 = This
        is
            a
        multiline string
    option2 = 
        and
        so is this

.. note:: The implementation doesn’t enforce all the option naming conventions yet

Let's parse the example:

.. sourcecode :: pycon

    >>> from configconvert import parse_config
    >>> options = parse_config('test.conf', 'utf8')
    >>> options
    {'mail[0].name': u'James', 'app.filename': 'test.conf', 'mail[1].name': u'Ian', 'mail[1].address': u'ian@example.com', 'mail[0].address': u'james@example.com', 'app.description': u'This is a\nmultiline\ndescription', 'app.title': u'My App', 'app.name': u'Application'}

The idea now is that you'll decode the data using NestedRecord:
 
.. sourcecode :: pycon

    >>> from nestedrecord import decode
    >>> decode(options)
    {'mail': [{'name': u'James', 'address': u'james@example.com'}, {'name': u'Ian', 'address': u'ian@example.com'}], 'app': {'filename': 'test.conf', 'description': u'This is a\nmultiline\ndescription', 'name': u'Application', 'title': u'My App'}}

