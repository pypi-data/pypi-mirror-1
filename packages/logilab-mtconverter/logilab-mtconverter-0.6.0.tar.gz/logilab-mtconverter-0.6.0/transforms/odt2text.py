"""odt2text: Turn odt file into equivalent plain text file.
Copyright (C) 2009 Logilab S.A.
"""
from zipfile import ZipFile
from lxml import etree
from tempfile import TemporaryFile as tmpfile

from logilab.mtconverter.transform import Transform

class odt_to_unformatted_text(Transform):
    """transforms odt content to unformatted plain text"""

    name = "odt_to_text"
    inputs  = ("application/vnd.oasis.opendocument.text",)
    output = "text/plain"

    def _convert(self, trdata):
        data = trdata.data
        # XXX ZipFile should also accept a string
        #     however, there is some bug within
        #     so we feed it a file
        if isinstance(data, str):
            tmp = tmpfile(mode='w+b')
            tmp.write(data)
            tmp.seek(0)
            data = tmp
        # /XXX
        zip = ZipFile(data, 'r')
        alltext = []
        for subelt in ('content.xml', 'meta.xml'):
            root = etree.fromstring(zip.read(subelt))
            for node in root.iter():
                for attr in ('text', 'tail'):
                    text = getattr(node, attr)
                    if text:
                        text = text.strip()
                        if text:
                            alltext.append(text)
        return u' '.join(alltext)
