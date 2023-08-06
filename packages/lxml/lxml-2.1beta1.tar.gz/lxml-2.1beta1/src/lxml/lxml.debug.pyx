cimport tree, xmlparser

cdef class MemChecker:
    cdef int _mem_use
    def __init__(self):
        self._mem_use = 0

    def prepare(self):
        xmlparser.xmlCleanupParser()
        self._mem_use = tree.xmlMemBlocks()
        xmlparser.xmlInitParser()

    def check(self):
        cdef int used
        xmlparser.xmlCleanupParser()
        used = tree.xmlMemBlocks()
        xmlparser.xmlInitParser()
        return used - self._mem_use
