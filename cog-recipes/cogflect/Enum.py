#!/usr/bin/env python

import cog

from cogflect.GeneratorBase import GeneratorBase
from cogflect.util import typedef, const, sanitizeTypename
from cogflect.common import generate_enum_common

class Enum(GeneratorBase):
    def __init__(self, name, fields):
        GeneratorBase.__init__(self, name, fields)

    def __gen_info_index(self, field, idx):
        cog.out("template<>\n"
                "struct info_index<%d>\n" % idx)
        cog.out("{\n")
        cog.out("    static const unsigned index = %d;\n" % idx)

        # TODO: Add test for this
        value = None
        if field.value != None:
            value = field.value
        else:
            value = idx

        cog.out("    static const int value = %d;\n" % value)
        cog.out("    inline static const char* string() { return \"%s::%s\"; }\n" % (self.name, field.name))

        if field.type != None:
            cog.out("    typedef %s type;\n" % sanitizeTypename(field.type))

        for t in self.possible_tags:
            if t in field.tags:
                cog.out("    typedef cogflect::true_t %s;\n" % t)
            else:
                cog.out("    typedef cogflect::false_t %s;\n" % t)

        for e in field.metadata:
            cog.out("    ")
            e.out()
            cog.out("\n")

        cog.out("};\n\n")

        cog.out("typedef info_index<%d> %s_INFO;" % (idx, field.name))

    def generate(self):
        generate_enum_common()

        cog.out("namespace " + self.name + " {")
        cog.out("\n\n")

        # Forward declare info_index templates
        cog.out("template<unsigned i>\n"
                "struct info_index;\n\n")

        for i, f in enumerate(self.fields):
            self.__gen_info_index(f, i)
            cog.out("\n\n")

        cog.out("// This is a constant rather than a function so that it\n"
                "// can be used as a template parameter. In C++0x we can change\n"
                "// it to be a function using the 'constexpr' keyword.\n")
        cog.out("static const unsigned size = %d;\n\n" % len(self.fields))

        cog.out("class type\n"
                "{\n"
                "private:\n"
                "    int val_;\n"
                "\n"
                "    explicit inline type(int val) : val_(val) {}\n"
                "\n"
                "public:\n"
                "    inline type(type const& other) : val_(other.val_) {}\n"
                "    inline type& operator=(type other) { val_ = other.val_; }\n"
                "\n"
                "    template<class Info>\n"
                "    static inline type make_from_info()\n"
                "    {\n"
                "        return type(Info::value);\n"
                "    }\n"
                "\n")

        cog.out("    template<class Action>\n"
                "    static inline void value_switcher(int value, Action& action)\n"
                "    {\n"
                "        switch(value)\n"
                "        {\n")

        for f in self.fields:
            cog.out("            case %s_INFO::value:\n" % f.name)
            cog.out("                action.template action< %s_INFO >();\n" % f.name)
            cog.out("                break;\n")

        cog.out("            default:\n"
                "                action.default_action();\n"
                "                break;\n")


        cog.out("        }\n" # close switch
                "    }\n\n") # close value_switcher

        cog.out("    template<class Action>\n"
                "    static inline void index_switcher(unsigned index, Action& action)\n"
                "    {\n"
                "        switch(index)\n"
                "        {\n")

        for f in self.fields:
            cog.out("            case %s_INFO::index:\n" % f.name)
            cog.out("                action.template action< %s_INFO >();\n" % f.name)
            cog.out("                break;\n")

        cog.out("            default:\n"
                "                action.default_action();\n"
                "                break;\n")


        cog.out("        }\n" # close switch
                "    }\n\n") # close index_switcher

        cog.out(""
                "    template<class Action>\n"
                "    inline void switcher(Action& action) const\n"
                "    {\n"
                "        value_switcher(val_, action);\n"
                "    }\n"
                "\n"
                "    inline int value() const\n"
                "    {\n"
                "        return val_;\n"
                "    }\n"
                "\n"
                "    inline unsigned index() const\n"
                "    {\n"
                "        cogflect::store_index_action sw;\n"
                "        switcher(sw);\n"
                "        return sw.index;\n"
                "    }\n"
                "\n"
                "    inline const char* string() const\n"
                "    {\n"
                "        cogflect::store_string_action sw;\n"
                "        switcher(sw);\n"
                "        return sw.str;\n"
                "    }\n"
                "\n")

        cog.out("    // This is a constant rather than a function so that it\n"
                "    // can be used as a template parameter. In C++0x we can change\n"
                "    // it to be a function using the 'constexpr' keyword.\n")
        cog.out("    static const unsigned size = %d;\n\n" % len(self.fields))

        cog.out("};\n\n") # close class

        cog.out("namespace {\n\n")
        for f in self.fields:
            cog.out("const type %s(type::make_from_info<%s_INFO>());\n" % (f.name, f.name))
        cog.out("\n}\n\n") # close anonymous namespace

        cog.out("}\n") # close enum namespace
