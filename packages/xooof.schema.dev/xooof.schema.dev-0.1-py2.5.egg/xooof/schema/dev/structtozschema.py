import os
import re

from xooof.spectools import Specs
from xooof.spectools import Field


class SChemaGenerator:

    def __init__(self, specs):
        self._specs = specs
        self.header = None

    @classmethod
    def getStructNameSpace(klass, object, key="python"):
        return object.structNs.getValue(key)

    @classmethod
    def getDescr(klass, obj, lang="en"):
        if len(obj.descr) == 0:
            return ""
        for descr in obj.descr:
            if descr.language == lang:
                return descr.description
        return obj.descr[0].description

    @classmethod
    def getStructName(klass, obj):
        return obj.className[1]

    @classmethod
    def _formatStructNameToSchemaName(klass, struct):
        return "I%s"%struct.className[1]

    @classmethod
    def _getAttributeType(klass, datatype):
        data_type = datatype.attrib.get(u"zope_attribute_type", None)
        if data_type is not None:
            return data_type
        if len(datatype.choices) > 0:
            return u"zope.schema.Choice"
        if datatype.datatype == "tstring":
            return u"zope.schema.TextLine"
        if datatype.datatype == "tint":
            return u"zope.schema.Int"
        if datatype.datatype == "tdecimal":
            return u"zope.schema.Float"
        if datatype.datatype == "tboolean":
            return "zope.schema.Bool"
        if datatype.datatype == "tcode":
            return u"zope.schema.Choice"
        if datatype.datatype == "tdatetime":
            return u"zope.schema.Datetime"
        if datatype.datatype == "tdate":
            return u"zope.schema.Date"
        if datatype.datatype == "ttime":
            return u"zope.schema.Time"
        if datatype.datatype == "tbinary":
            return u"zope.schema.Bytes"

    @classmethod
    def _stringToStringValue(klass, field, value):
        if field.datatype.datatype in ("tstring", "tcode"):
            return u'"%s"'%value
        if field.datatype.datatype == "tint":
            return u"%ld"%long(value)
        if field.datatype.datatype == "tdecimal":
            fractionDigits = field.datatype.fractionDigits
            format = u"%%.%df" % fractionDigits
            if not fractionDigits:
                pattern = re.compile(r"\s*[-+]?[0-9]+\s*$")
            else:
                pattern = re.compile(r"\s*[-+]?[0-9]+(\.[0-9]{1,%d})?\s*$" \
                        % fractionDigits)
            if pattern.match(value) is None:
                raise ValueError("invalid decimal literal or too many " \
                                  "fraction digits (max %d): %s" % \
                                  (fractionDigits, value))
                return format%float(value)
        if field.datatype.datatype == "tboolean":
            try:
                return u"%s"%bool(value)
            except:
                ValueError("Invalid boolean literal (%s)" % value)
        if field.datatype.datatype in ("tdatetime", "tdate", "ttime"):
            raise NotImplementedError("tdate...")

    @classmethod
    def _getListLength(klass, field):
        formattedString = u""
        if field.minOccur is not None:
            formattedString += u"""
        min_length=%s,"""%field.minOccur
        if field.maxOccur is not None:
            formattedString += u"""
        max_length=%s,"""%field.maxOccur
        return formattedString

    @classmethod
    def _formatCommonFieldProperties(klass, field, struct):
        formattedName = klass._formatStructNameToSchemaName(struct).lower()
        prefix = klass.getStructNameSpace(struct) or ""
        prefix = prefix.replace(".", "_")
        formattedString = u"""
        title=_(u"%s_%s_%s",
            default=u"%s"), """%(prefix,
                              formattedName,
                              field.name,
                              klass.getDescr(field)) + """
        description=_(u"%s_%s_%s_help",
            default=u""),"""%(prefix, formattedName, field.name)
        return formattedString

    @classmethod
    def _getVocabularyName(klass, vocabulary):
        return vocabulary.split(".")[-1]

    @classmethod
    def _getVocabularyModule(klass, vocabulary):
        return ".".join(vocabulary.split(".")[:-1])

    @classmethod
    def _formatDataTypeProperties(klass, datatype, field, struct, indent=2):
        formattedString = u""
        if datatype.datatype == "tcode":
            indent_string = "".zfill(indent * 4).replace("0", " ")
            formattedString += u"\n%svocabulary='%s',"% \
                    (indent_string, datatype.name)
            return formattedString

        indent_string = "".zfill(indent * 4).replace("0", " ")
        vocabulary_name = datatype.attrib.get(u"zope_vocabulary_source",
                None)
        if vocabulary_name is not None:
            formattedString += u"\n%ssource='%s',"% \
                    (indent_string, vocabulary_name)
            return formattedString
        vocabulary_name = datatype.attrib.get(u"zope_vocabulary_name",
                None)
        if vocabulary_name is not None:
            formattedString += u"\n%svocabulary='%s',"% \
                    (indent_string, vocabulary_name)
            return formattedString
        vocabulary = datatype.attrib.get(u"zope_vocabulary", None)
        if vocabulary is not None:
            formattedString += u"\n%svocabulary=%s,"% \
                    (indent_string, klass._getVocabularyName(vocabulary))
            return formattedString

        if len(datatype.choices) > 0:
            formattedString += u"\n%svocabulary=zope.schema.vocabulary" \
            ".SimpleVocabulary([" % \
                    indent_string
            indent_string = "".zfill(indent+2 * 4).replace("0", " ")
            prefix = klass.getStructNameSpace(struct) or ""
            prefix = prefix.replace(".", "_")
            formattedName = klass._formatStructNameToSchemaName(struct).lower()
            for choice in datatype.choices:
                choice_value = u'u"%s"'%choice.value
                choice_i18n_code = "%s_%s_%s_%s"% (
                        prefix, formattedName, field.name, choice.value)
                choice_title = u'_(u"%s", default=u"%s")'% (
                        choice_i18n_code, klass.getDescr(choice))
                formattedString +=u"\n%szope.schema.vocabulary" \
                ".SimpleTerm(%s, title=%s)," %(indent_string,
                        choice_value,
                        choice_title)
            formattedString += u"]),"
            return formattedString
        indent_string = "".zfill(indent * 4).replace("0", " ")
        if datatype.datatype in ("tdate", "tdatetime", "ttime", "tboolean"):
            return ""
        if datatype.datatype == "tstring":
            if datatype.minLen is not None:
                formattedString += u"\n%smin_length=%s," \
                        %(indent_string, datatype.minLen)
            if datatype.maxLen is not None:
                formattedString += u"\n%smax_length=%s," \
                        %(indent_string, datatype.maxLen)
        if datatype.datatype in ("tint", "tdecimal"):
            if datatype.minVal is not None:
                formattedString += u"\n%smin=%s," \
                        %(indent_string, datatype.minVal)
            if datatype.maxVal is not None:
                formattedString += u"\n%smax=%s," \
                        %(indent_string, datatype.maxVal)
        return formattedString

    def _getAllStructToImport(self, struct):
        allStructs = []
        if struct.baseClass is not None:
            allStructs.append(self._specs.getStruct(struct.baseClass))
        for field in struct.fields:
            if not field.fieldType in (Field.GLFIELD, Field.GFIELD):
                continue
            allStructs.append(self._specs.getStruct(field.className))
        return allStructs

    def _formatVFieldProperty(self, field, struct):
        value_type = self._getAttributeType(field.datatype)
        formattedString = u"""
    %s = %s(""" %(field.name, value_type) + \
        self._formatCommonFieldProperties(field, struct) + \
        self._formatDataTypeProperties(field.datatype, field, struct)
        required = u"True"
        if not field.mandatory:
            required = u"False"
        formattedString += u"""
        required=%s,""" %required
        if field.default is not None:
            formattedString += u"""
        default=%s,""" %self._stringToStringValue(field.default)
        formattedString += u"""
        )
"""
        return formattedString

    def _formatVLFieldProperty(self, field, struct):
        value_type = self._getAttributeType(field.datatype)
        formattedString = u"""
    %s = zope.schema.List(""" %field.name + \
        self._formatCommonFieldProperties(field, struct) + \
        self._getListLength(field) + u"""
        value_type = %s( """ % value_type + \
        self._formatDataTypeProperties(field.datatype, field, struct, 3) +u"""
            )
        )
"""
        return formattedString

    def _formatGFieldProperty(self, field, struct):
        dataStruct = (self._specs.getStruct(field.className))
        schema = self._formatStructNameToSchemaName(dataStruct)
        formattedString = u"""
    %s = zope.schema.Object(""" %field.name + u"""
        schema=%s,"""%schema + \
        self._formatCommonFieldProperties(field, struct)
        required = u"True"
        if not field.mandatory:
            required = u"False"
            formattedString += u"""
        required=%s,""" %required
        formattedString += u"""
        )
"""
        return formattedString

    def _formatGLFieldProperty(self, field, struct):
        dataStruct = (self._specs.getStruct(field.className))
        schema = self._formatStructNameToSchemaName(dataStruct)
        formattedString = u"""
    %s = zope.schema.List(""" %field.name + u"""
        value_type = zope.schema.Object(schema=%s),"""%schema + \
        self._formatCommonFieldProperties(field, struct)
        formattedString += self._getListLength(field) + u"""
        )
"""
        return formattedString

    def _generateStruct(self, fileName, struct, messageFactory):
        print ("generate %s to %s"%(struct.specFile, fileName))
        f = open(fileName, "w")
        try:
            f.write(self.header)
            f.write(u"import zope.interface\n")
            attributeModules = {"zope.schema": None}
            for field in struct.fields:
                if hasattr(field, "datatype"):
                    value_type = self._getAttributeType(field.datatype)
                    attributeModules[".".join(value_type.split(".")[:-1])]=None
                    vocabulary = field.attrib.get("zope_vocabulary", None)
                    if vocabulary is not None:
                        attributeModules[
                                self._getVocabularyModule(vocabulary)] = None
            for module in attributeModules.keys():
                f.write(u"import %s\n"%module)
            if struct.baseClass is None:
                f.write(u"from zope.interface import Interface\n\n")
            f.write("%s as _\n\n"%(messageFactory))
            for subStruct in self._getAllStructToImport(struct):
                f.write(u"from %s.interfaces.%s import %s\n"%
                        (self.getStructNameSpace(subStruct),
                         self.getStructName(subStruct).lower(),
                         self._formatStructNameToSchemaName(subStruct)),
                    )
            formattedName = self._formatStructNameToSchemaName(struct)
            if struct.baseClass:
                f.write(u"\nclass %s(%s):\n"%(
                    formattedName,
                    self._formatStructNameToSchemaName(
                        self._specs.getStruct(struct.baseClass)),
                    ))
            else:
                f.write(u"\nclass %s(Interface):\n"%formattedName)
            f.write(u'    zope.interface.taggedValue("xmlns","%s")\n' \
                    %self.getStructNameSpace(struct, "xml"))
            for field in struct.fields:
                if field.fieldType == Field.VFIELD:
                    f.write(self._formatVFieldProperty(field,
                        struct).encode("utf-8"))
                elif field.fieldType == Field.VLFIELD:
                    f.write(u"%s\n"%self._formatVLFieldProperty(field, struct))
                elif field.fieldType == Field.GFIELD:
                    f.write(u"%s\n"%self._formatGFieldProperty(field, struct))
                elif field.fieldType == Field.GLFIELD:
                    f.write(u"%s\n"%self._formatGLFieldProperty(field, struct))
        finally:
            f.close()

    def generate(self, outputDir, messageFactory, structNames, structns,
            copyingFile):
        self.header = u"# -*- coding: utf-8 -*-\n"
        if copyingFile is not None and \
                os.path.exists(copyingFile):
            f = open(copyingFile, "r")
            try:
                self.header += f.readlines()
            finally:
                f.close()
        self.header += u"""# This code was generated by the struct2zchema \
tool from the Xooof framework.
# The script is distributed as part of the xooof.schema.dev module
# see http://www.xooof.org
# Changes to this file may cause incorrect behavior and will be lost if
# the code is regenerated.
"""
        if not os.path.exists(outputDir):
            raise Exception("Path does not exist '%s' "%outputDir)
        allStructs = self._specs.getAllStructs()
        if structNames is not None and \
                len(structNames):
            allStructs = [struct for struct in allStructs if
                    self.getStructName(struct) in structNames]
        if structns is not None:
            allStructs = [struct for struct in allStructs if
                    self.getStructNameSpace(struct) == structns]
        for struct in allStructs:
            fileName = self.getStructName(struct).lower()
            fileName = os.path.join(outputDir, "%s.py"%fileName)
            self._generateStruct(fileName, struct, messageFactory)

        if structns is not None:
            init_file = open(os.path.join(outputDir, "__init__.py"), "w")
            try:
                init_file.write(self.header)
                for struct in allStructs:
                    init_file.write("from %s.interfaces.%s import %s\n"%
                            (self.getStructNameSpace(struct),
                                self.getStructName(struct).lower(),
                                self._formatStructNameToSchemaName(struct)))
            finally:
                init_file.close()


def main():
    import sys
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options], struct1, "
            "struct2, ...")
    parser.add_option("-c", "--copying-file", action="store",
        dest="copyingFile", type="string", nargs=1,
        help="File containing the copying to add on top of the generated file"
                "Be carefull, the copying must be formatted as python"
                "comments")
    parser.add_option("-s", "--struct-specs-dir", action="append",
        dest="structSpecsDir", type="string", nargs=1,
        help="The directory containing the structs specifications")
    parser.add_option("-o", "--output-dir", action="store",
        dest="outputDir", type="string", nargs=1,
        help="The output directory")
    parser.add_option("-n", "--struct-name", action="append",
        dest="structNames", type="string", nargs=1,
        help="The name of the struct to process. If not given, "\
                "all structs for the given python structns will be generated")
    parser.add_option("-m", "--structns", action="store",
        dest="structns", type="string", nargs=1,
        help="Only struct parts of this structns (python module name) "\
                "will be generated")
    parser.add_option("-f", "--message-factory", action="store",
        dest="messageFactory", type="string", nargs=1,
        help="The MessageFactory class to use for i18n ex "\
                "(from x.y import MessageFactory)")

    options, args = parser.parse_args()
    if options.structSpecsDir is None or \
            not len(options.structSpecsDir) or \
            not options.outputDir or \
            not options.messageFactory:
        parser.print_help()
        sys.exit(1)

    specs = Specs(options.structSpecsDir)
    generator = SChemaGenerator(specs)
    generator.generate(options.outputDir,
            options.messageFactory,
            options.structNames,
            options.structns,
            options.copyingFile)

if __name__ == "__main__":
    main()
