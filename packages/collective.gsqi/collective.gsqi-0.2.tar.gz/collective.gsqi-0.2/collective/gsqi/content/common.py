import cStringIO
import ConfigParser

class PropertiesStructureAdapter(object):

    def _getPropsParser(self, id, subdir, import_context,
                        defaults={}):
        properties = import_context.readDataFile(
            '.properties', '%s/%s' % (subdir, id))
        if properties is not None:
            stream = cStringIO.StringIO(properties)
            parser = ConfigParser.ConfigParser(defaults=defaults)
            parser.optionxform = str # case sensitive
            parser.readfp(stream)
            return parser
