import os
from tempfile import mkstemp

from logilab.mtconverter import MissingBinary
from logilab.mtconverter.transform import Transform

bin_search_path = [path for path in os.environ['PATH'].split(os.pathsep)
                   if os.path.isdir(path)]


def bin_search(binary):
    """search the bin_search_path for a given binary returning its fullname or
       raises MissingBinary"""
    result = None
    mode   = os.R_OK | os.X_OK
    for path in bin_search_path:
        pathbin = os.path.join(path, binary)
        if os.access(pathbin, mode) == 1:
            return pathbin
            break
    raise MissingBinary('Unable to find binary "%s" in %s' % 
                        (binary, os.pathsep.join(bin_search_path)))


class POpenTransform(Transform):
    """abstract class for external command based transform

    The external command may read from stdin but must write to stdout
    If use_stdin is False, a temporary file will be used as input for
    the command
    """

    cmdname = None
    cmdargs = ""
    use_stdin = True
    input_encoding = None
    #output_encoding = 'utf-8'

    def __init__(self, name=None, binary=None, cmdargs=None, use_stdin=None,
                 **kwargs):
        if name is not None:
            self.name = name
        if binary is not None:
            self.binary = bin_search(binary)
        else:
            self.binary = bin_search(self.cmdname)
        if cmdargs is not None:
            self.cmdargs = cmdargs
        if use_stdin is not None:
            self.use_stdin = use_stdin

    def _command_line(self, trdata):
        return "%s %s" % (self.binary, self.cmdargs)
        
    def _convert(self, trdata):
        command = self._command_line(trdata)
        data = trdata.encode(self.input_encoding)
        if not self.use_stdin:
            tmpfile, tmpname = mkstemp(text=False) # create tmp
            os.write(tmpfile, data) # write data to tmp using a file descriptor
            os.close(tmpfile)       # close it so the other process can read it
            command = command % {'infile' : tmpname} # apply tmp name to command
        cin, couterr = os.popen4(command, 'b')
        if self.use_stdin:
            cin.write(data)
        status = cin.close()
        out = couterr.read()
        couterr.close()
        if not self.use_stdin:
            # remove tmp file
            os.unlink(tmpname)
        return out.strip()


class pdf_to_text(POpenTransform):
    name = "pdf_to_text"
    inputs = ('application/pdf',)
    output = 'text/plain'
    output_encoding = 'utf-8'

    cmdname = "pdftotext"
    cmdargs = "%(infile)s -enc UTF-8 -"
    use_stdin = False


class lynx_dump(POpenTransform):
    name = "lynx_dump"
    inputs = ('text/html', 'text/xhtml')
    output = 'text/plain'
    
    cmdname = "lynx"
    cmdargs = "-dump -stdin"
    use_stdin = True

    def _command_line(self, trdata):
        encoding = trdata.encoding
        if encoding == 'ascii':
            encoding = 'iso-8859-1' # lynx doesn't know ascii !
        return '%s %s -assume_charset=%s -display_charset=%s' % (
            self.binary, self.cmdargs, encoding, encoding)
        

transform_classes = [pdf_to_text] # , lynx_dump]
