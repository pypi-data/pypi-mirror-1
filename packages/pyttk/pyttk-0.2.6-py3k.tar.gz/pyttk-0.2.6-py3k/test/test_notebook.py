import unittest
import tkinter
import ttk

import support

class NotebookTest(unittest.TestCase):

    def setUp(self):
        self.nb = ttk.Notebook()
        self.child1 = ttk.Label()
        self.child2 = ttk.Label()
        self.nb.add(self.child1, text='a')
        self.nb.add(self.child2, text='b')

    def tearDown(self):
        self.child1.destroy()
        self.child2.destroy()
        self.nb.destroy()


    def test_tab_identifiers(self):
        self.nb.forget(0)
        self.nb.hide(self.child2)
        self.failUnlessRaises(tkinter.TclError, self.nb.tab, self.child1)
        self.failUnlessEqual(self.nb.index('end'), 1)
        self.nb.add(self.child2)
        self.failUnlessEqual(self.nb.index('end'), 1)
        self.nb.select(self.child2)

        self.failUnless(self.nb.tab('current'))
        self.nb.add(self.child1, text='a')

        self.nb.pack()
        self.nb.wait_visibility()
        self.failUnlessEqual(self.nb.tab('@5,5'), self.nb.tab('current'))

        for i in range(5, 100, 5):
            if self.nb.tab('@%d, 5' % i, text=None) == 'a':
                break
        else:
            self.fail("Tab with text 'a' not found")


    def test_add_and_hidden(self):
        self.failUnlessRaises(tkinter.TclError, self.nb.hide, -1)
        self.failUnlessRaises(tkinter.TclError, self.nb.hide, 'hi')
        self.failUnlessRaises(tkinter.TclError, self.nb.hide, None)
        self.failUnlessRaises(tkinter.TclError, self.nb.add, None)
        self.failUnlessRaises(tkinter.TclError, self.nb.add, ttk.Label(),
            unknown='option')

        tabs = self.nb.tabs()
        self.nb.hide(self.child1)
        self.nb.add(self.child1)
        self.failUnlessEqual(self.nb.tabs(), tabs)

        child = ttk.Label()
        self.nb.add(child, text='c')
        tabs = self.nb.tabs()

        curr = self.nb.index('current')
        # verify that the tab gets readded at its previous position
        child2_index = self.nb.index(self.child2)
        self.nb.hide(self.child2)
        self.nb.add(self.child2)
        self.failUnlessEqual(self.nb.tabs(), tabs)
        self.failUnlessEqual(self.nb.index(self.child2), child2_index)
        self.failUnless(str(self.child2) == self.nb.tabs()[child2_index])
        # but the tab next to it (not hidden) is the one selected now
        self.failUnlessEqual(self.nb.index('current'), curr + 1)


    def test_forget(self):
        self.failUnlessRaises(tkinter.TclError, self.nb.forget, -1)
        self.failUnlessRaises(tkinter.TclError, self.nb.forget, 'hi')
        self.failUnlessRaises(tkinter.TclError, self.nb.forget, None)

        tabs = self.nb.tabs()
        child1_index = self.nb.index(self.child1)
        self.nb.forget(self.child1)
        self.failIf(str(self.child1) in self.nb.tabs())
        self.failUnlessEqual(len(tabs) - 1, len(self.nb.tabs()))

        self.nb.add(self.child1)
        self.failUnlessEqual(self.nb.index(self.child1), 1)
        self.failIf(child1_index == self.nb.index(self.child1))


    def test_index(self):
        self.failUnlessRaises(tkinter.TclError, self.nb.index, -1)
        self.failUnlessRaises(tkinter.TclError, self.nb.index, None)

        self.failUnless(isinstance(self.nb.index('end'), int))
        self.failUnlessEqual(self.nb.index(self.child1), 0)
        self.failUnlessEqual(self.nb.index(self.child2), 1)
        self.failUnlessEqual(self.nb.index('end'), 2)


    def test_insert(self):
        # moving tabs
        tabs = self.nb.tabs()
        self.nb.insert(1, tabs[0])
        self.failUnlessEqual(self.nb.tabs(), (tabs[1], tabs[0]))
        self.nb.insert(self.child1, self.child2)
        self.failUnlessEqual(self.nb.tabs(), tabs)
        self.nb.insert('end', self.child1)
        self.failUnlessEqual(self.nb.tabs(), (tabs[1], tabs[0]))
        self.nb.insert('end', 0)
        self.failUnlessEqual(self.nb.tabs(), tabs)
        # bad moves
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, 2, tabs[0])
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, -1, tabs[0])

        # new tab
        child3 = ttk.Label()
        self.nb.insert(1, child3)
        self.failUnlessEqual(self.nb.tabs(), (tabs[0], str(child3), tabs[1]))
        self.nb.forget(child3)
        self.failUnlessEqual(self.nb.tabs(), tabs)
        self.nb.insert(self.child1, child3)
        self.failUnlessEqual(self.nb.tabs(), (str(child3), ) + tabs)
        self.nb.forget(child3)
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, 2, child3)
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, -1, child3)

        # bad inserts
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, 'end', None)
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, None, 0)
        self.failUnlessRaises(tkinter.TclError, self.nb.insert, None, None)


    def test_select(self):
        self.nb.pack()
        self.nb.wait_visibility()

        success = []
        tab_changed = []

        self.child1.bind('<Unmap>', lambda evt: success.append(True))
        self.nb.bind('<<NotebookTabChanged>>',
            lambda evt: tab_changed.append(True))

        self.failUnlessEqual(self.nb.select(), str(self.child1))
        self.nb.select(self.child2)
        self.failUnless(success)
        self.failUnlessEqual(self.nb.select(), str(self.child2))

        self.nb.update()
        self.failUnless(tab_changed)


    def test_tab(self):
        self.failUnlessRaises(tkinter.TclError, self.nb.tab, -1)
        self.failUnlessRaises(tkinter.TclError, self.nb.tab, 'notab')
        self.failUnlessRaises(tkinter.TclError, self.nb.tab, None)

        self.failUnless(isinstance(self.nb.tab(self.child1), dict))
        self.failUnlessEqual(self.nb.tab(self.child1, text=None), 'a')
        self.nb.tab(self.child1, text='abc')
        self.failUnlessEqual(self.nb.tab(self.child1, text=None), 'abc')


    def test_tabs(self):
        self.failUnlessEqual(len(self.nb.tabs()), 2)

        self.nb.forget(self.child1)
        self.nb.forget(self.child2)

        self.failUnlessEqual(self.nb.tabs(), ())


    def test_traversal(self):
        self.nb.pack()
        self.nb.wait_visibility()

        self.nb.select(0)

        support.simulate_mouse_click(self.nb, 5, 5)
        self.nb.event_generate('<Control-Tab>')
        self.failUnlessEqual(self.nb.select(), str(self.child2))
        self.nb.event_generate('<Shift-Control-Tab>')
        self.failUnlessEqual(self.nb.select(), str(self.child1))
        self.nb.event_generate('<Shift-Control-Tab>')
        self.failUnlessEqual(self.nb.select(), str(self.child2))

        self.nb.tab(self.child1, text='a', underline=0)
        self.nb.enable_traversal()
        self.nb.event_generate('<Alt-a>')
        self.failUnlessEqual(self.nb.select(), str(self.child1))


def test_main():
    support.run(NotebookTest)

if __name__ == "__main__":
    test_main()
