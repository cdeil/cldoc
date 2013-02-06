from node import Node
from method import Method
from root import Root
from ctype import Type
from cldoc.clang import cindex

class Class(Node):
    kind = cindex.CursorKind.CLASS_DECL

    class Base:
        def __init__(self, cursor, access):
            self.cursor = cursor
            self.access = access
            self.type = Type(cursor.type)
            self.node = None

    def __init__(self, cursor, comment):
        Node.__init__(self, cursor, comment)

        self.process_children = True
        self.current_access = cindex.CXXAccessSpecifier.PRIVATE
        self.bases = []
        self.subclasses = []
        self.name_to_method = {}

    def resolve_bases(self, mapping):
        for b in self.bases:
            tpname = b.type.typename

            if tpname in mapping:
                b.node = mapping[tpname]
                b.node.subclasses.append(self)

    def append(self, child):
        Node.append(self, child)

        if isinstance(child, Method):
            self.name_to_method[child.name] = child

    @property
    def methods(self):
        for child in self.children:
            if isinstance(child, Method):
                yield child

    def visit(self, cursor, citer):
        if cursor.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
            self.current_access = cursor.access_specifier
            return []
        elif cursor.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
            # Add base
            self.bases.append(Class.Base(cursor.type.get_declaration(), cursor.access_specifier))
            return []

        return Node.visit(self, cursor, citer)

# vi:ts=4:et