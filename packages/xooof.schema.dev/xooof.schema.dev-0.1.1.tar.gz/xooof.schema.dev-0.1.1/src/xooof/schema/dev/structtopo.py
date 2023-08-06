"""structopo performs various tasks related to xml struct files.

Unless the -h, or --help option is given one of the commands below must be
present:
    sync:
       Parse all xml files and add translation for each new entry found.
       If a msgid already exist in the pot file, the translation is not
       replaced.

    force-sync:
        Same as sync but, replace translation into the pot file by those
        coming from struct files

"""
import os
from xooof.spectools import Specs
from xooof.spectools import Field
from i18ndude import catalog

LANGUAGE_DICT = {
        "en": "english",
        "fr": "french",
        }
doc = __doc__


class PoGenerator:

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
        found = False
        for descr in obj.descr:
            if descr.language == lang:
                description = descr.description
                found = True
        if not found:
            description = obj.descr[0].description
        #remove carriage return
        lines = [line.strip() for line in description.split("\n")]
        return " ".join(lines)

    @classmethod
    def getStructName(klass, obj):
        return obj.className[1]

    @classmethod
    def _formatStructNameToSchemaName(klass, struct):
        return "I%s"%struct.className[1]

    def _update_catalog(self, ctl, struct, lang):
        for field in struct.fields:
            formattedName = self._formatStructNameToSchemaName(struct).lower()
            prefix = self.getStructNameSpace(struct) or ""
            prefix = prefix.replace(".", "_")
            msgid = u"%s_%s_%s"%(prefix, formattedName, field.name)
            msgstr = self.getDescr(field, lang)
            ctl.add(msgid, msgstr, references=[struct.specFile])
            #output_stream.write(formattedString.encode("utf-8"))
            if field.fieldType in (Field.VFIELD, Field.VLFIELD) and \
                    len(field.datatype.choices) > 0:
                vocabulary_name = field.datatype.attrib.get(
                        u"zope_vocabulary_name",
                        None)
                if vocabulary_name is None:
                    for choice in field.datatype.choices:
                        choice_msgid = u"%s_%s_%s_%s"% (
                            prefix, formattedName, field.name, choice.value)
                        choice_msgstr = self.getDescr(choice, lang)
                        ctl.add(choice_msgid, choice_msgstr,
                                references=[struct.specFile])

    def generate(self, pot_fn, struct_names, structns,
            lang, create_domain=None, force=True):

        if not os.path.exists(pot_fn):
            orig_ctl = catalog.MessageCatalog(domain=create_domain)
        else:
            orig_ctl = catalog.MessageCatalog(filename=pot_fn)

        struct_ctl = catalog.MessageCatalog(domain=create_domain)


        allStructs = self._specs.getAllStructs()
        if struct_names is not None and \
                len(struct_names):
            allStructs = [struct for struct in allStructs if
                    self.getStructName(struct) in struct_names]
        if structns is not None:
            allStructs = [struct for struct in allStructs if
                    self.getStructNameSpace(struct) == structns]

        #output_stream = open(outputFile, "w")
        for struct in allStructs:
            self._update_catalog(struct_ctl, struct, lang)
        if not force:
            orig_ctl.add_missing(struct_ctl)
        else:
            for key, val in struct_ctl.items():
                old_value = orig_ctl.get(key, val)
                old_value.msgstr = val.msgstr
                comments = [c for c in val.comments if c not in
                        old_value.comments]
                old_value.comments.extend(comments)
                references = [ref for ref in val.references if ref not in
                        old_value.references]
                old_value.references.extend(references)
                automatic_comments = [ac for ac in val.automatic_comments
                        if ac not in old_value.automatic_comments]
                old_value.automatic_comments.extend(automatic_comments)
                orig_ctl[key] = old_value

        orig_ctl.mime_header['PO-Revision-Date'] = catalog.now()
        orig_ctl.mime_header['Language-Code'] = lang
        orig_ctl.mime_header['Language-Name'] = LANGUAGE_DICT.get(
                lang, 'unknow')
        f = open(pot_fn, 'w')
        try:
            writer = catalog.POWriter(f, orig_ctl)
            writer.write(msgstrToComment=False)
        finally:
            f.close()


def main(*args, **kwargs):
    import sys
    from optparse import OptionParser
    parser = OptionParser(usage=doc+ ""
            "usage: %prog [options], struct1, "
            "struct2, ...")
    parser.add_option("-s", "--struct-specs-dir", action="append",
        dest="struct_specs_dir", type="string", nargs=1,
        help="The directory containing the structs specifications")
    parser.add_option("-p", "--pot", action="store",
        dest="pot_fn", type="string", nargs=1,
        help="The output pot file")
    parser.add_option("-l", "--lang", action="store",
        dest="lang", type="string", nargs=1,
        help="The target lang for the translation string")
    parser.add_option("-c", "--create", action="store",
        dest="create_domain", type="string", nargs=1,
        help="If given and the pot file does'nt exist, create a new one for "
        "the given domain")
    parser.add_option("-n", "--struct-name", action="append",
        dest="struct_names", type="string", nargs=1,
        help="The name of the struct to process. If not given, "\
                "all structs for the given python structns will be parsed")
    parser.add_option("-m", "--structns", action="store",
        dest="structns", type="string", nargs=1,
        help="Only struct parts of this structns (python module name) "\
                "will be generated")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    command = sys.argv[1]
    if command not in ("sync", "force-sync"):
        parser.print_help()
        sys.exit(1)
    options, args = parser.parse_args()
    if options.struct_specs_dir is None or \
            not len(options.struct_specs_dir) or \
            not options.pot_fn or \
            not options.lang or \
            not options.create_domain:
        parser.print_help()
        sys.exit(1)
    if not os.path.exists(options.pot_fn) and \
            not options.create_domain:
        parser.print_help()
        sys.exit(1)

    force = command == "force-sync"
    specs = Specs(options.struct_specs_dir)
    generator = PoGenerator(specs)

    generator.generate(options.pot_fn,
            options.struct_names,
            options.structns,
            options.lang,
            options.create_domain,
            force)

if __name__ == "__main__":
    main()
