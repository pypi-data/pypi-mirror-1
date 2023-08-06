"""\
ConfigConvert is a set of ConversionKit converters designed specifically to
help you create Python objects from options set in a text file.
"""

import logging
import os

log = logging.getLogger(__name__)

from configconvert.internal import eval_import, simple_import, import_module
from bn import uniform_path as up

#
# ConversionKit handlers
#

def stringToObject():
    """\
    Takes a string written in the format ``"path.to.module:object"`` and 
    returns the object.
    """
    def stringToObject_converter(conversion, state):
        value = conversion.value
        try:
            result = eval_import(value)
        except ImportError, e:
            conversion.error = (
                'Could not import object %r specified in the config '
                'file. The error was %s'
            )%(value, str(e))
        else:
            conversion.result = result
    return stringToObject_converter

#
# File Handling Converters
#    

def existingDirectory(
    try_to_create=False, 
    raise_on_create_error=False,
    uniform_path=False,
):
    """\
    Ensure the directory specified as the input exists and is not a file, 
    otherwise set an error.

    If ``try_to_create`` is ``True``, the converter will try to create the
    directory if it doesn't exist. In that case you can set
    ``raise_on_create_error`` to ``True`` to have any problems creating the
    directory trigger an exception instead of setting a conversion error.

    If the directory exists (or has been created) the directory path is set
    as the conversion result. If ``uniform_path`` is set to ``True``, the 
    absolute, normalized path is set instead of the value given as the input.
    """
    def existingDirectory_converter(conversion, state):
        directory = conversion.value
        if not os.path.exists(directory):
            if try_to_create:
                # Try to create it
                try:
                    os.mkdir(directory)
                except:
                    if raise_on_create_error:
                        raise
                    conversion.error = 'Could not create the directory %r' % (
                        directory
                    )
                else:
                    if uniform_path:
                        conversion.result = up(directory)
                    else:
                        conversion.result = directory
            else:
                conversion.error = 'The directory doesn\'t exist'
        elif not os.path.isdir(directory):
            conversion.error = 'The path is not a directory'
        else:
            if uniform_path:
                conversion.result = up(directory)
            else:
                conversion.result = directory
    return existingDirectory_converter

def existingFile(
    try_to_create=False, 
    raise_on_create_error=False, 
    file_content='',
    uniform_path=False,
):
    """\
    Ensure the file specified as the input exists and is not a directory, 
    otherwise set an error.

    If ``try_to_create`` is ``True``, the converter will try to create the file
    if it doesn't exist with the content ``file_content`` which defaults to `''``.
    The file is opened with mode ``'wb'`` (write binary) so the contents of
    ``file_content`` should be a binary string in the encoding you wish to use. If
    the content is an ordinary Python string, that is fine. If it is a Unicode
    string you'll need to encode it to an appropriate format first. For example: 

    ::

        existingFile(try_to_create=True, file_content=unicode_string.encode('utf8'))

    If you have set ``try_to_create`` to ``True`` you can set
    ``raise_on_create_error`` to ``True`` so that any problems which are encountered
    when creating the file trigger an exception instead of setting a conversion error.

    If the file exists (or has been created) the file path is set as the conversion
    result. If ``uniform_path`` is set to ``True``, the 
    absolute, normalized path is set instead of the value given as the input.
    """
    def existingFile_converter(conversion, state):
        filename = conversion.value
        if not os.path.exists(filename):
            if try_to_create:
                # Try to create it
                try:
                    fp = open(filename, 'wb')
                    fp.write(file_content)
                    fp.close()
                except:
                    if raise_on_create_error:
                        raise
                    conversion.error = 'Could not create the file %r' % (
                        filename
                    )
                else:
                    if uniform_path:
                        conversion.result = up(filename)
                    else:
                        conversion.result = filename
            else:
                conversion.error = 'The file doesn\'t exist'
        elif os.path.isdir(filename):
            conversion.error = 'The path is not a file'
        else:
            if uniform_path:
                conversion.result = up(filename)
            else:
                conversion.result = filename
    return existingFile_converter

# This isn't a post-converter and I'm not sure where it would be used
##
## Post-converters
##
#
#def attribute_dict(conversion, state):
#    # No point in importing it unless it is needed
#    from powerpack.util import AttributeDict
#    conversion.result = AttributeDict(conversion.value)

#
# Parse Config
#

def parse_config(filename, encoding='utf8'):
    r"""\
    Parse a config file with a strict format.

    The config file is made of options and values which are each defined on a
    single line terminated by a ``\n`` character and separtated by only the 
    three characters `` = ``. For example

    ::

        option = value

    The parsed config file results in a dictionary with the options as ASCII
    strings for the keys and the values as unicode strings for the values. The
    options must start with the letters a-z, A-Z or _ and should contain only
    letters, numbers or the ``_`` character. Thus the option values
    have the same naming rules as Python variables.

    If you don't leave a space each side of the ``=`` character it is considered
    a syntax error. Any extra space characters after the space
    after the equals sign are treated as part of the value. For example this::

        option =  value
   
    would result in the option ``'option'`` taking the value ``u' value'``. 
    Any extra spaces after the option name are ignored though.

    The file must use UNIX style line endings (ie each line ends in ``\n``) and
    must be encoded as UTF-8. Values can therefore take any Unicode character as
    long as the file is encoded correctly.

    You can also specify multiline values. You do so by specifying the first 
    line of the multiline value on the same line as the option starting 
    immediately after the space after the equals sign (once again any extra spaces
    will be treated as part of the value). All subsequent lines have to be 
    indented 4 spaces. Any characters after those 4 spaces are treated as part
    of the line. In fact the first line doesn't have to contain any text if you
    are using a multiline value, in which case the value will start with a ``\n``
    character. Here are two examples::

        option1 = This
            is
                a
            multiline string
        option2 = 
            and
            so is this

    Note: The implementation doesn't enforce all the option naming conventions
    yet
    """
    fp = None
    try:
        # Open in binary mode to avoid Python doing clever things with line
        # endings
        fp = open(filename, 'rb')
        data = fp.read().decode('utf-8')
        fp.close()
        fp = None
        conf = {}
        cur_option = None
        cur_value = None
        for i, line in enumerate(data.split('\n')):
             if line.startswith('#'):
                 # It is a comment
                 continue
             elif line.startswith('    '):
                 if i == 0:
                     raise SyntaxError('Line %s cannot start with four '
                         'spaces', i+1)
                 # It is either a mistake, blank line or part of a multiline
                 # value
                 elif option is None:
                     raise SyntaxError('Indented line found but no option '
                         'specified')
                 else:
                     # It is part of a multiline string
                     cur_value.append(line[4:])
             elif not line.strip():
                 # Assume it is the end of a multiline string:
                 if cur_option is not None:
                     conf[str(cur_option)] = '\n'.join(cur_value)
                     cur_option = None
                     cur_value = None
                 continue
             elif (ord(line[0]) >= 65 and ord(line[0])<=90) or \
                (ord(line[0]) >= 97 and ord(line[0])<=122) or \
                ord(line[0]) == 95:
                 # It is the start of an option
                 parts = line.split(' = ')
                 if len(parts) == 1:
                     error = "Expected the characters ' = ' on line %s"
                     if '=' in line:
                         error += ", not just an '=' on its own"
                     raise SyntaxError(error%i+1)
                 elif len(parts) > 2:
                     value = ' = '.join(parts[1:])
                 else:
                     value = parts[1]
                 # Extra whitespace after the option is ignored 
                 option = parts[0].strip()
                 if conf.has_key(option):
                     raise SyntaxError(
                         'The option %s found on line %s was already '
                         'specified earlier in the file'%(option, i+1)
                     )
                 # Add the previous config option
                 if cur_option is not None:
                     conf[str(cur_option)] = '\n'.join(cur_value)
                 cur_option = option
                 cur_value = [value]
             else:
                 raise SyntaxError(
                     'Unexpected character at the start of line %s'%i+1) 
        # Add the last config option
        if cur_option is not None:
            conf[cur_option] = '\n'.join(cur_value)
        if not conf.has_key('app.filename'):
            conf['app.filename'] = filename
    finally:
        if fp:
            fp.close()
    return conf

