import codecs
import os
import sys

from silme.core.object import *
import silme.format

try:
    import chardet
    char_detector=True
except ImportError:
    char_detector=False

class IOClient(object):
    bomdict = { 'utf_8_sig' : codecs.BOM_UTF8,
                'utf_16_be' : codecs.BOM_UTF16_BE,
                'utf_16_le' : codecs.BOM_UTF16_LE,
                'utf_16' : codecs.BOM_UTF16 }

    @classmethod
    def matches_path(cls, path):
        """
        tests if the ioclient should be used for this type of path
        """
        raise NotImplementedError()

    @classmethod
    def get_blob (cls, path, source=True):
        raise NotImplementedError()

    @classmethod
    def get_entitylist (cls, path, source=False, code='default', parser=None):
        raise NotImplementedError()

    @classmethod
    def get_l10nobject (cls, path, source=False, code='default', parser=None):
        raise NotImplementedError()

    @classmethod
    def get_l10npackage (cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        raise NotImplementedError()

    @classmethod
    def get_source(cls, path, encoding=None, fallback=None):
        """
        reads source from the path
        """
        raise NotImplementedError()

    @classmethod
    def get_source_with_encoding(cls, path, encoding):
        """
        reads source with encoding fallback
        """
        raise NotImplementedError()

    @classmethod
    def get_source_without_encoding(cls, path):
        """
        reads source ignoring encoding (in binary compatible mode)
        """
        raise NotImplementedError()

    @classmethod
    def write_blob(cls, blob, path):
        raise NotImplementedError()

    @classmethod
    def write_entitylist(cls, elist, path):
        raise NotImplementedError()

    @classmethod
    def write_l10nobject(cls, l10nobject, path):
        raise NotImplementedError()

    @classmethod
    def write_object(cls, object, path):
        raise NotImplementedError()

    @classmethod
    def write_l10npackage(cls, l10npackage, path):
        raise NotImplementedError()

    @classmethod
    def write_source(cls, source, path, encoding):
        """
        writes source to destination path
        """
        raise NotImplementedError()

    @classmethod
    def path_type(cls, path):
        """
        returns 'package', 'object' depending on the path type
        """
        raise NotImplementedError()


class FileFormatClient(IOClient):

    @classmethod
    def get_blob(cls, path, uri=None, source=True):
        blob = Blob()
        blob.id = os.path.basename(path)
        if source:
            blob.source = cls.get_source_without_encoding(path)
        blob.uri = uri or path
        return blob

    @classmethod
    def get_entitylist(cls, path, uri=None, source=False, code='default', parser=None):
        if not parser:
            parser = silme.format.Manager.get(path=path)
        src = cls.get_source(path, encoding = parser.encoding,
                            fallback = parser.fallback)
        entitylist = parser.get_entitylist(src[0], code=code)
        entitylist.id = os.path.basename(path)
        entitylist.uri = uri or path
        if source:
            entitylist.source = src[0]
        entitylist.encoding = src[1]
        return entitylist

    @classmethod
    def get_l10nobject(cls, path, uri=None, source=False, code='default', parser=None):
        if not parser:
            parser = silme.format.Manager.get(path=path)
        src = cls.get_source(path, encoding = parser.encoding,
                            fallback = parser.fallback)
        l10nobject = parser.get_l10nobject(src[0], code=code)
        l10nobject.id = os.path.basename(path)
        l10nobject.uri = uri or path
        if source:
            l10nobject.source = src[0]
        l10nobject.encoding = src[1]
        return l10nobject

    @classmethod
    def get_l10npackage(cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        l10npackage = L10nPackage()
        l10npackage.id = os.path.basename(path)
        l10npackage.uri = path
        return l10npackage

    @classmethod
    def get_source(cls, path, encoding=None, fallback=None):
        """
        reads source with all autoguessing, encoding guessing.
        This methods is offered for reading sources that are semantically
        meaningfull for later use.
        """
        # if the encoding parameter is specified, force it to being used
        # There is no fallback if opening with this encoding fails!
        if encoding is not None:
            output = cls.get_source_with_encoding(path, encoding)
            if output[1] != encoding and (fallback is None or 
                                        output[1] not in fallback):
                raise Exception('The encoding for path ' + path + ' is not ' + \
                                encoding + ' like expected, but ' + output[1] + \
                                '. ' + output[1] + ' is not in the fallback list' + \
                                ', break.')
            return output
        else:
            # if no encoding specified, try the fallback list
            if fallback is None or len(fallback) is 0:
                fallback = ['utf_8']
            for coding in fallback:
                try:
                    return cls.get_source_with_encoding(path, coding)
                except IOError, e:
                    raise
                except UnicodeDecodeError, e:
                    continue # TODO: logging
            # if we still did not succeed, try to check if the BOM is specified
            text = cls._read_without_encoding(path)
            for coding, bom in cls.bomdict.items():
                if text.startswith(bom):
                    try:
                        return cls.get_source_with_encoding(path, coding)
                    except UnicodeError, e:
                        raise
            # UniversalDetector: only used if available
            # When used, a slow down of 10 to 20 times can be expected!
            # Be warned: sometimes it detects the encoding wrongly!
            if char_detector:
                try:
                    coding=\
                    chardet.detect(cls.read_without_encoding(path))['encoding'].lower()
                except Exception, e:
                    pass # TODO: logging
                else:
                    try:
                        return cls.get_source_with_encoding(path, coding)
                    except UnicodeDecodeError, e:
                        pass # TODO: logging
            # last chance: try to open using the system default encoding
            try:
                return cls.get_source_with_encoding(path, sys.getdefaultencoding())
            except Exception, e:
                return (cls.get_source_without_encoding(path), None)

    @classmethod
    def get_source_with_encoding(cls, path, encoding):
        try:
            text = cls._read_with_encoding(path, encoding)
        except UnicodeDecodeError, e:
            raise
        except IOError, e:
            raise IOError(path + ': ' + str(e))
        except Exception, e:
            raise
        else:
            text, encoding = cls._test_bom(text, encoding)
            if isinstance(text, str):
                return cls._to_unicode(text, encoding)
            else:
                return (text, encoding)

    @classmethod
    def get_source_without_encoding(cls, path):
        try:
            return cls._read_without_encoding(path)
        except IOError, e:
            raise IOError(path + ': ' + str(e))
        except Exception, e:
            raise

    @classmethod
    def _test_bom(cls, text, encoding):
        # unichr(65279) == \ufeff == Unicode BOM as text
        if encoding == 'utf_8' and text.startswith(unichr(65279)):
            text = text[len(unichr(65279)):]
            encoding = 'utf_8_sig'
        elif encoding in cls.bomdict.keys() and text.startswith(unichr(65279)):
            text = text[len(unichr(65279)):]
        elif encoding == 'utf_8_sig' and not text.startswith(unichr(65279)):
            encoding = 'utf_8'
        return (text, encoding)

    @classmethod
    def _to_unicode(cls, text, encoding):
        # we want to work only on unicode strings!
        try:
            decode_to_unicode = codecs.getdecoder(encoding)
            text = decode_to_unicode(text)[0]
        except UnicodeEncodeError, e:
            raise
        return (text, encoding)

    @staticmethod
    def _get_source_policy(source):
        # returns two variables that define whether the source of a file
        # should be attached to a given object
        #
        # if source is True - l10nobject,entitylist and blob get source
        # if source is False - none of them gets source
        # if source is None - l10nobject and entity list get it, blob does not
        if source is None:
            b_source = True # blob source
            oe_source = False # l10nobject & entitylist source
        elif source is False: # don't load it for anyone
            b_source = False
            oe_source = False
        else: # load it for everyone
            b_source = True
            oe_source = True
        return (b_source, oe_source)
    
    @staticmethod
    def _should_ignore(ignore, path, elems):
        # allows objects and packages to be ignored inside get_l10npackage.
        #
        # ignore argument of IOClient.get_l10npackage can be:
        # list - list of files and directories to ignore
        # function - in which case the function will be launched against each
        #            object or package load
        if ignore.__class__.__name__=='function': # is function
            return ignore(query)
        else:
            return any([i in ignore for i in elems])

    @classmethod
    def _write_source_with_encoding(cls, content, path, encoding=None):
        raise NotImplementedError()
    
    @classmethod
    def _read_with_encoding(cls, path, encoding):
        raise NotImplementedError()

    @classmethod
    def _read_without_encoding(cls, path):
        raise NotImplementedError()

class DBClient (IOClient):
    get_blob = None
    get_l10nobject = None
    write_blob = None
    write_l10nobject = None
    write_source = None

    def get_entitylist (cls, path):
        raise NotImplementedError()

    @classmethod
    def write_object(cls, object, path, encoding=None):
        if isinstance(object, EntityList):
            cls.write_entitylist(object, path, encoding=encoding)
        else:
            raise TypeError()

class RCSClient (FileFormatClient):
    pass
