from lib2to3 import fixer_base
import symbol as syms

class FixTest(fixer_base.BaseFix):

    explicit = True

    def match(self, node):
        return node.type == syms.file_input or node.type == syms.single_input

    def transform(self, node, results):
        for each in node.pre_order():
            print repr(each)
