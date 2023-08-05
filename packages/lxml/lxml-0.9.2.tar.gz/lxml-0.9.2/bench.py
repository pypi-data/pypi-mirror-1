import sys, string, time, copy, gc
from itertools import *

_TEXT  = "some ASCII text"
_UTEXT = u"some klingon: \F8D2"
_ATTRIBUTES = {
    '{attr}test' : _UTEXT,
    'bla'        : _TEXT
    }

def with_attributes(use_attributes):
    "Decorator for benchmarks that use attributes"
    value = {False : 0, True : 1}[ bool(use_attributes) ]
    def set_value(function):
        try:
            function.ATTRIBUTES.add(value)
        except AttributeError:
            function.ATTRIBUTES = set([value])
        return function
    return set_value

def with_text(no_text=False, text=False, utext=False):
    "Decorator for benchmarks that use text"
    values = []
    if no_text:
        values.append(0)
    if text:
        values.append(1)
    if utext:
        values.append(2)
    def set_value(function):
        try:
            function.TEXT.add(values)
        except AttributeError:
            function.TEXT = set(values)
        return function
    return set_value

def onlylib(*libs):
    def set_libs(function):
        if libs:
            function.LIBS = libs
        return function
    return set_libs


class BenchMarkBase(object):
    atoz = string.ascii_lowercase

    _LIB_NAME_MAP = {
        'etree'        : 'lxe',
        'ElementTree'  : 'ET',
        'cElementTree' : 'cET'
        }

    def __init__(self, etree):
        self.etree = etree
        libname = etree.__name__.split('.')[-1]
        self.lib_name = self._LIB_NAME_MAP.get(libname, libname)

        if libname == 'etree':
            deepcopy = copy.deepcopy
            def set_property(root, fname):
                setattr(self, fname, lambda : deepcopy(root))
        else:
            def set_property(root, fname):
                setattr(self, fname, self.et_make_factory(root))

        attribute_list = list(izip(count(), ({}, _ATTRIBUTES)))
        text_list = list(izip(count(), (None, _TEXT, _UTEXT)))
        build_name = self._tree_builder_name

        self.setup_times = []
        for tree in self._all_trees():
            times = []
            self.setup_times.append(times)
            setup = getattr(self, '_setup_tree%d' % tree)
            for an, attributes in attribute_list:
                for tn, text in text_list:
                    root, t = setup(text, attributes)
                    times.append(t)
                    set_property(root, build_name(tree, tn, an))

    def _tree_builder_name(self, tree, tn, an):
        return '_root%d_T%d_A%d' % (tree, tn, an)

    def tree_builder(self, tree, tn, an):
        return getattr(self, self._tree_builder_name(tree, tn, an))

    def et_make_factory(self, elem):
        def generate_elem(append, elem, level):
            var = "e" + str(level)
            arg = repr(elem.tag)
            if elem.attrib:
                arg += ", **%r" % elem.attrib
            if level == 1:
                append(" e1 = Element(%s)" % arg)
            else:
                append(" %s = SubElement(e%d, %s)" % (var, level-1, arg))
            if elem.text:
                append(" %s.text = %r" % (var, elem.text))
            if elem.tail:
                append(" %s.tail = %r" % (var, elem.tail))
            for e in elem:
                generate_elem(append, e, level+1)
        # generate code for a function that creates a tree
        output = ["def element_factory():"]
        generate_elem(output.append, elem, 1)
        output.append(" return e1")
        # setup global function namespace
        namespace = {
            "Element"    : self.etree.Element,
            "SubElement" : self.etree.SubElement
            }
        # create function object
        exec "\n".join(output) in namespace
        return namespace["element_factory"]

    def _all_trees(self):
        all_trees = []
        for name in dir(self):
            if name.startswith('_setup_tree'):
                all_trees.append(int(name[11:]))
        return all_trees

    def _setup_tree1(self, text, attributes):
        "tree with 26 2nd level and 520 3rd level children"
        atoz = self.atoz
        SubElement = self.etree.SubElement
        current_time = time.time
        t = current_time()
        root = self.etree.Element('{a}root')
        for ch1 in atoz:
            el = SubElement(root, "{b}"+ch1, attributes)
            for ch2 in atoz:
                for i in range(20):
                    SubElement(el, "{c}%s%03d" % (ch2, i))
        t = current_time() - t
        return (root, t)

    def _setup_tree2(self, text, attributes):
        "tree with 520 2nd level and 26 3rd level children"
        atoz = self.atoz
        SubElement = self.etree.SubElement
        current_time = time.time
        t = current_time()
        root = self.etree.Element('{a}root')
        for ch1 in atoz:
            for i in range(20):
                el = SubElement(root, "{b}"+ch1, attributes)
                for ch2 in atoz:
                    SubElement(el, "{c}%s%03d" % (ch2, i))
        t = current_time() - t
        return (root, t)

    def _setup_tree3(self, text, attributes):
        "tree of depth 8 with 3 children per node"
        SubElement = self.etree.SubElement
        current_time = time.time
        t = current_time()
        root = self.etree.Element('{a}root')
        children = [root]
        for i in range(7):
            tag_no = count().next
            children = [ SubElement(c, "{b}a%d" % i, attributes)
                         for i,c in enumerate(chain(children, children, children)) ]
        t = current_time() - t
        return (root, t)

    def _setup_tree4(self, text, attributes):
        "small tree with 26 2nd level and 2 3rd level children"
        atoz = self.atoz
        SubElement = self.etree.SubElement
        current_time = time.time
        t = current_time()
        root = self.etree.Element('{a}root')
        children = [root]
        for ch1 in atoz:
            el = SubElement(root, "{b}"+ch1, attributes)
            SubElement(el, "{c}a", attributes)
            SubElement(el, "{c}b", attributes)
        t = current_time() - t
        return (root, t)

    def benchmarks(self):
        """Returns a list of all benchmarks.

        A benchmark is a tuple containing a method name and a list of tree
        numbers.  Trees are prepared by the setup function.
        """
        all_trees = self._all_trees()
        benchmarks = []
        for name in dir(self):
            if not name.startswith('bench_'):
                continue
            method = getattr(self, name)
            if hasattr(method, 'LIBS') and self.lib_name not in method.LIBS:
                benchmarks.append((name, None, (), 0, 0))
                continue
            if method.__doc__:
                tree_sets = method.__doc__.split()
            else:
                tree_sets = ()
            if tree_sets:
                tree_tuples = [ map(int, tree_set.split(','))
                                for tree_set in tree_sets ]
            else:
                try:
                    function = getattr(method, 'im_func', method)
                    arg_count = method.func_code.co_argcount - 1
                except AttributeError:
                    arg_count = 1
                tree_tuples = self._permutations(all_trees, arg_count)

            for tree_tuple in tree_tuples:
                for tn in sorted(getattr(method, 'TEXT', (0,))):
                    for an in sorted(getattr(method, 'ATTRIBUTES', (0,))):
                        benchmarks.append((name, method, tree_tuple, tn, an))

        return benchmarks

    def _permutations(self, seq, count):
        def _permutations(prefix, remainder, count):
            if count == 0:
                return [ prefix[:] ]
            count -= 1
            perms = []
            prefix.append(None)
            for pos, el in enumerate(remainder):
                new_remainder = remainder[:pos] + remainder[pos+1:]
                prefix[-1] = el
                perms.extend( _permutations(prefix, new_remainder, count) )
            prefix.pop()
            return perms
        return _permutations([], seq, count)


############################################################
# Benchmarks
############################################################

class BenchMark(BenchMarkBase):
    def bench_iter_children(self, root):
        for child in root:
            pass

    def bench_iter_children_reversed(self, root):
        for child in reversed(root):
            pass

    def bench_append_from_document(self, root1, root2):
        # == "1,2 2,3 1,3 3,1 3,2 2,1" # trees 1 and 2, or 2 and 3, or ...
        for el in root2:
            root1.append(el)

    def bench_insert_from_document(self, root1, root2):
        for el in root2:
            root1.insert(len(root1)/2, el)

    def bench_rotate_children(self, root):
        # == "1 2 3" # runs on any single tree independently
        for i in range(100):
            el = root[0]
            del root[0]
            root.append(el)

    def bench_reorder(self, root):
        for i in range(1,len(root)/2):
            el = root[0]
            del root[0]
            root[-i:-i] = [ el ]

    def bench_reorder_slice(self, root):
        for i in range(1,len(root)/2):
            els = root[0:1]
            del root[0]
            root[-i:-i] = els

    def bench_clear(self, root):
        root.clear()

    def bench_has_children(self, root):
        for child in root:
            if child and child and child and child and child:
                pass

    def bench_len(self, root):
        for child in root:
            map(len, repeat(child, 20))

    def bench_create_subelements(self, root):
        SubElement = self.etree.SubElement
        for child in root:
            SubElement(child, '{test}test')

    def bench_append_elements(self, root):
        Element = self.etree.Element
        for child in root:
            el = Element('{test}test')
            child.append(el)

    def bench_makeelement(self, root):
        Element = self.etree.Element
        empty_attrib = {}
        for child in root:
            child.makeelement('{test}test', empty_attrib)

    def bench_replace_children(self, root):
        Element = self.etree.Element
        for child in root:
            el = Element('{test}test')
            child[:] = [el]

    def bench_remove_children(self, root):
        for child in root:
            root.remove(child)

    def bench_remove_children_reversed(self, root):
        for child in reversed(root[:]):
            root.remove(child)

    def bench_set_attributes(self, root):
        for child in root:
            child.set('a', 'bla')

    @with_attributes(True)
    def bench_get_attributes(self, root):
        for child in root:
            child.set('a', 'bla')
        for child in root:
            child.get('a')

    def bench_setget_attributes(self, root):
        for child in root:
            child.set('a', 'bla')
        for child in root:
            child.get('a')

    def bench_getchildren(self, root):
        for child in root:
            child.getchildren()

    def bench_get_children_slice(self, root):
        for child in root:
            child[:]

    def bench_get_children_slice_2x(self, root):
        for child in root:
            children = child[:]
            child[:]

    def bench_deepcopy(self, root):
        for child in root:
            copy.deepcopy(child)

    def bench_tag(self, root):
        for child in root:
            child.tag

    def bench_tag_repeat(self, root):
        for child in root:
            for i in repeat(0, 100):
                child.tag

    @with_text(utext=True, text=True, no_text=True)
    def bench_text(self, root):
        for child in root:
            child.text

    @with_text(utext=True, text=True, no_text=True)
    def bench_text_repeat(self, root):
        repeat = range(500)
        for child in root:
            for i in repeat:
                child.text

    def bench_index(self, root):
        for child in root:
            root.index(child)

    def bench_index_slice(self, root):
        for child in root[5:100]:
            root.index(child, 5, 100)

    def bench_index_slice_neg(self, root):
        for child in root[-100:-5]:
            root.index(child, start=-100, stop=-5)

    def bench_getiterator(self, root):
        list(islice(root.getiterator(), 10, 110))

    def bench_getiterator_tag(self, root):
        list(islice(root.getiterator("{b}a"), 3, 10))

    def bench_getiterator_tag_all(self, root):
        list(root.getiterator("{b}a"))

    @onlylib('lxe')
    def bench_xpath_class(self, root):
        xpath = self.etree.XPath("./*[0]")
        for child in root:
            xpath(child)

    @onlylib('lxe')
    def bench_xpath_element(self, root):
        for child in root:
            xpath = self.etree.XPathElementEvaluator(child)
            xpath.evaluate("./*[0]")

############################################################
# Main program
############################################################

if __name__ == '__main__':
    import_lxml = True
    if len(sys.argv) > 1:
        try:
            sys.argv.remove('-i')
            sys.path.insert(0, 'src')
        except ValueError:
            pass

        try:
            sys.argv.remove('-nolxml')
            import_lxml = False
        except ValueError:
            pass

    _etrees = []
    if import_lxml:
        from lxml import etree
        _etrees.append(etree)

    if len(sys.argv) > 1:
        try:
            sys.argv.remove('-a')
        except ValueError:
            pass
        else:
            try:
                from elementtree import ElementTree as ET
                _etrees.append(ET)
            except ImportError:
                pass

            try:
                import cElementTree as cET
                _etrees.append(cET)
            except ImportError:
                pass

    if not _etrees:
        print "No library to test. Exiting."
        sys.exit(1)

    print "Preparing test suites and trees ..."

    benchmark_suites = map(BenchMark, _etrees)

    # sorted by name and tree tuple
    benchmarks = [ sorted(b.benchmarks()) for b in benchmark_suites ]

    if len(sys.argv) > 1:
        selected = []
        for name in sys.argv[1:]:
            if not name.startswith('bench_'):
                name = 'bench_' + name
            selected.append(name)
        benchmarks = [ [ b for b in bs if b[0] in selected ]
                       for bs in benchmarks ]

    import time
    def run_bench(suite, method_name, method_call, tree_set, tn, an):
        current_time = time.time
        call_repeat = range(10)

        tree_builders = [ suite.tree_builder(tree, tn, an)
                          for tree in tree_set ]

        times = []
        args = ()
        for i in range(3):
            gc.collect()
            gc.disable()
            t = 0
            for i in call_repeat:
                args = [ build() for build in tree_builders ]
                t_one_call = current_time()
                method_call(*args)
                t += current_time() - t_one_call
            t = 1000.0 * t / len(call_repeat)
            times.append(t)
            gc.enable()
            del args
        return times

    def build_treeset_name(trees, tn, an):
        text = {0:'-', 1:'S', 2:'U'}[tn]
        attr = {0:'-', 1:'A'}[an]
        return "%s%s T%s" % (text, attr, ',T'.join(imap(str, trees))[:6])


    print "Running benchmark on", ', '.join(b.lib_name
                                            for b in benchmark_suites)
    print

    print "Setup times for trees in seconds:"
    for b in benchmark_suites:
        print "%-3s:    " % b.lib_name,
        for an in (0,1):
            for tn in (0,1,2):
                print '  %s  ' % build_treeset_name((), tn, an)[:2],
        print
        for i, tree_times in enumerate(b.setup_times):
            print "     T%d:" % (i+1), ' '.join("%6.4f" % t for t in tree_times)
    print

    for bench_calls in izip(*benchmarks):
        for lib, (bench, benchmark_setup) in enumerate(izip(benchmark_suites, bench_calls)):
            bench_name, method_call = benchmark_setup[:2]
            tree_set_name = build_treeset_name(*benchmark_setup[-3:])
            print "%-3s: %-23s" % (bench.lib_name, bench_name[6:29]),
            if method_call is None:
                print "skipped"
                continue

            print "(%-10s)" % tree_set_name,
            sys.stdout.flush()

            result = run_bench(bench, *benchmark_setup)

            for t in result:
                print "%9.4f" % t,
            print "msec/pass, best: %9.4f" % min(result)

        if len(benchmark_suites) > 1:
            print # empty line between different benchmarks
