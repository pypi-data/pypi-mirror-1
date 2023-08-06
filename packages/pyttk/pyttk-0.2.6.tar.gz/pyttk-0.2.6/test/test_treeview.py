import unittest
import Tkinter
import ttk

import support
from test_functions import MockTclObj, MockStateSpec

class TreeviewTest(unittest.TestCase):

    def setUp(self):
        self.tv = ttk.Treeview()

    def tearDown(self):
        self.tv.destroy()


    def test_bbox(self):
        self.tv.pack()
        self.failUnlessEqual(self.tv.bbox(''), '')
        self.tv.wait_visibility()
        self.tv.update()

        item_id = self.tv.insert('', 'end')
        children = self.tv.get_children()
        self.failUnless(children)

        bbox = self.tv.bbox(children[0])
        self.failUnlessEqual(len(bbox), 4)
        self.failUnless(isinstance(bbox, tuple))
        for item in bbox:
            if not isinstance(item, int):
                self.fail("Invalid bounding box: %s" % bbox)
                break

        # compare width in bboxes
        self.tv['columns'] = ['test']
        self.tv.column('test', width=50)
        bbox_column0 = self.tv.bbox(children[0], 0)
        root_width = self.tv.column('#0', width=None)
        self.failUnlessEqual(bbox_column0[0], bbox[0] + root_width)

        # verify that bbox of a closed item is the empty string
        child1 = self.tv.insert(item_id, 'end')
        self.failUnlessEqual(self.tv.bbox(child1), '')


    def test_children(self):
        # no children yet, should get an empty tuple
        self.failUnlessEqual(self.tv.get_children(), ())

        item_id = self.tv.insert('', 'end')
        self.failUnless(isinstance(self.tv.get_children(), tuple))
        self.failUnlessEqual(self.tv.get_children()[0], item_id)

        # add item_id and child3 as children of child2
        child2 = self.tv.insert('', 'end')
        child3 = self.tv.insert('', 'end')
        self.tv.set_children(child2, item_id, child3)
        self.failUnlessEqual(self.tv.get_children(child2), (item_id, child3))

        # child3 has child2 as parent, thus trying to set child2 as a children
        # of child3 should result in an error
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.set_children, child3, child2)

        # remove child2 children
        self.tv.set_children(child2)
        self.failUnlessEqual(self.tv.get_children(child2), ())

        # remove root's children
        self.tv.set_children('')
        self.failUnlessEqual(self.tv.get_children(), ())


    def test_column(self):
        # return a dict with all options/values
        self.failUnless(isinstance(self.tv.column('#0'), dict))
        # return a single value of the given option
        self.failUnless(isinstance(self.tv.column('#0', width=None), int))
        # set a new value for an option
        self.tv.column('#0', width=10)
        self.failUnlessEqual(self.tv.column('#0', width=None), 10)
        # check read-only option
        self.failUnlessRaises(Tkinter.TclError, self.tv.column, '#0', id='X')

        self.failUnlessRaises(Tkinter.TclError, self.tv.column, 'invalid')
        invalid_kws = [
            {'unknown_option': 'some value'},  {'stretch': 'wrong'},
            {'anchor': 'wrong'}, {'width': 'wrong'}, {'minwidth': 'wrong'}
        ]
        for kw in invalid_kws:
            self.failUnlessRaises(Tkinter.TclError, self.tv.column, '#0',
                **kw)


    def test_delete(self):
        self.failUnlessRaises(Tkinter.TclError, self.tv.delete, '#0')

        item_id = self.tv.insert('', 'end')
        item2 = self.tv.insert(item_id, 'end')
        self.failUnlessEqual(self.tv.get_children(), (item_id, ))
        self.failUnlessEqual(self.tv.get_children(item_id), (item2, ))

        self.tv.delete(item_id)
        self.failIf(self.tv.get_children())

        # reattach should fail
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.reattach, item_id, '', 'end')


    def test_detach_reattach(self):
        item_id = self.tv.insert('', 'end')
        item2 = self.tv.insert(item_id, 'end')

        # calling detach without items is valid, although it does nothing
        prev = self.tv.get_children()
        self.tv.detach() # this should do nothing
        self.failUnlessEqual(prev, self.tv.get_children())

        self.failUnlessEqual(self.tv.get_children(), (item_id, ))
        self.failUnlessEqual(self.tv.get_children(item_id), (item2, ))

        # detach item with children
        self.tv.detach(item_id)
        self.failIf(self.tv.get_children())

        # reattach item with children
        self.tv.reattach(item_id, '', 'end')
        self.failUnlessEqual(self.tv.get_children(), (item_id, ))
        self.failUnlessEqual(self.tv.get_children(item_id), (item2, ))

        # move a children to the root
        self.tv.move(item2, '', 'end')
        self.failUnlessEqual(self.tv.get_children(), (item_id, item2))
        self.failUnlessEqual(self.tv.get_children(item_id), ())

        # bad values
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.reattach, 'nonexistant', '', 'end')
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.detach, 'nonexistant')
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.reattach, item2, 'otherparent', 'end')
        self.failUnlessRaises(Tkinter.TclError,
            self.tv.reattach, item2, '', 'invalid')

        # multiple detach
        self.tv.detach(item_id, item2)
        self.failUnlessEqual(self.tv.get_children(), ())
        self.failUnlessEqual(self.tv.get_children(item_id), ())


    def test_exists(self):
        self.failUnlessEqual(self.tv.exists('something'), False)
        self.failUnlessEqual(self.tv.exists(''), True)
        self.failUnlessEqual(self.tv.exists({}), False)

        # the following will make a tk.call equivalent to
        # tk.call(treeview, "exists") which should result in an error
        # in the tcl interpreter since tk requires an item.
        self.failUnlessRaises(Tkinter.TclError, self.tv.exists, None)


    def test_focus(self):
        # nothing is focused right now
        self.failUnlessEqual(self.tv.focus(), '')

        item1 = self.tv.insert('', 'end')
        self.tv.focus(item1)
        self.failUnlessEqual(self.tv.focus(), item1)

        self.tv.delete(item1)
        self.failUnlessEqual(self.tv.focus(), '')

        # try focusing inexistant item
        self.failUnlessRaises(Tkinter.TclError, self.tv.focus, 'hi')


    def test_heading(self):
        # check a dict is returned
        self.failUnless(isinstance(self.tv.heading('#0'), dict))

        # check a value is returned
        self.tv.heading('#0', text='hi')
        self.failUnlessEqual(self.tv.heading('#0', text=None), 'hi')

        # invalid option
        self.failUnlessRaises(Tkinter.TclError, self.tv.heading, '#0',
            background=None)
        # invalid value
        self.failUnlessRaises(Tkinter.TclError, self.tv.heading, '#0',
            anchor=1)


    def test_heading_callback(self):
        def simulate_heading_click(x, y):
            support.simulate_mouse_click(self.tv, x, y)
            self.tv.update_idletasks()

        success = [] # no success for now

        self.tv.pack()
        self.tv.wait_visibility()
        self.tv.heading('#0', command=lambda: success.append(True))
        self.tv.column('#0', width=100)
        self.tv.update()

        # assuming that the coords (5, 5) fall into heading #0
        simulate_heading_click(5, 5)
        if not success:
            self.fail("The command associated to the treeview heading wasn't "
                "invoked.")

        success = []
        commands = self.tv.master._tclCommands
        self.tv.heading('#0', command=str(self.tv.heading('#0', command=None)))
        self.failUnlessEqual(commands, self.tv.master._tclCommands)
        simulate_heading_click(5, 5)
        if not success:
            self.fail("The command associated to the treeview heading wasn't "
                "invoked.")

        # XXX The following raises an error in a tcl interpreter, but not in
        # Python
        #self.tv.heading('#0', command='I dont exist')
        #simulate_heading_click(5, 5)


    def test_index(self):
        # item 'what' doesn't exist
        self.failUnlessRaises(Tkinter.TclError, self.tv.index, 'what')

        self.failUnlessEqual(self.tv.index(''), 0)

        item1 = self.tv.insert('', 'end')
        item2 = self.tv.insert('', 'end')
        c1 = self.tv.insert(item1, 'end')
        c2 = self.tv.insert(item1, 'end')
        self.failUnlessEqual(self.tv.index(item1), 0)
        self.failUnlessEqual(self.tv.index(c1), 0)
        self.failUnlessEqual(self.tv.index(c2), 1)
        self.failUnlessEqual(self.tv.index(item2), 1)

        self.tv.move(item2, '', 0)
        self.failUnlessEqual(self.tv.index(item2), 0)
        self.failUnlessEqual(self.tv.index(item1), 1)

        # check that index still works even after its parent and siblings
        # have been detached
        self.tv.detach(item1)
        self.failUnlessEqual(self.tv.index(c2), 1)
        self.tv.detach(c1)
        self.failUnlessEqual(self.tv.index(c2), 0)

        # but it fails after item has been deleted
        self.tv.delete(item1)
        self.failUnlessRaises(Tkinter.TclError, self.tv.index, c2)


    def test_insert_item(self):
        # parent 'none' doesn't exist
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, 'none', 'end')

        # open values
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, '', 'end',
            open='')
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, '', 'end',
            open='please')
        self.failIf(self.tv.delete(self.tv.insert('', 'end', open=True)))
        self.failIf(self.tv.delete(self.tv.insert('', 'end', open=False)))

        # invalid index
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, '', 'middle')

        # trying to duplicate item id is invalid
        itemid = self.tv.insert('', 'end', 'first-item')
        self.failUnlessEqual(itemid, 'first-item')
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, '', 'end',
            'first-item')
        self.failUnlessRaises(Tkinter.TclError, self.tv.insert, '', 'end',
            MockTclObj('first-item'))

        # unicode values
        value = u'\xe1ba'
        item = self.tv.insert('', 'end', values=(value, ))
        self.failUnlessEqual(self.tv.item(item, values=None), (value, ))

        self.tv.item(item, values=list(self.tv.item(item, values=None)))
        self.failUnlessEqual(self.tv.item(item, values=None), (value, ))

        self.failUnless(isinstance(self.tv.item(item), dict))

        # erase item values
        self.tv.item(item, values='')
        self.failIf(self.tv.item(item, values=None))

        # item tags
        item = self.tv.insert('', 'end', tags=[1, 2, value])
        self.failUnlessEqual(self.tv.item(item, tags=None), ('1', '2', value))
        self.tv.item(item, tags=[])
        self.failIf(self.tv.item(item, tags=None))
        self.tv.item(item, tags=(1, 2))
        self.failUnlessEqual(self.tv.item(item, tags=None), ('1', '2'))

        # values with spaces
        item = self.tv.insert('', 'end', values=('a b c',
            '%s %s' % (value, value)))
        self.failUnlessEqual(self.tv.item(item, values=None),
            ('a b c', '%s %s' % (value, value)))

        # text
        self.failUnlessEqual(self.tv.item(
            self.tv.insert('', 'end', text="Label here"), text=None),
            "Label here")
        self.failUnlessEqual(self.tv.item(
            self.tv.insert('', 'end', text=value), text=None),
            value)


    def test_set(self):
        self.tv['columns'] = ['A', 'B']
        item = self.tv.insert('', 'end', values=['a', 'b'])
        self.failUnlessEqual(self.tv.set(item), {'A': 'a', 'B': 'b'})

        self.tv.set(item, 'B', 'a')
        self.failUnlessEqual(self.tv.item(item, values=None), ('a', 'a'))

        self.tv['columns'] = ['B']
        self.failUnlessEqual(self.tv.set(item), {'B': 'a'})

        self.tv.set(item, 'B', 'b')
        self.failUnlessEqual(self.tv.set(item, column='B'), 'b')
        self.failUnlessEqual(self.tv.item(item, values=None), ('b', 'a'))

        self.tv.set(item, 'B', 123)
        self.failUnlessEqual(self.tv.set(item, 'B'), 123)
        self.failUnlessEqual(self.tv.item(item, values=None), (123, 'a'))
        self.failUnlessEqual(self.tv.set(item), {'B': 123})

        # inexistant column
        self.failUnlessRaises(Tkinter.TclError, self.tv.set, item, 'A')
        self.failUnlessRaises(Tkinter.TclError, self.tv.set, item, 'A', 'b')

        # inexistant item
        self.failUnlessRaises(Tkinter.TclError, self.tv.set, 'notme')


    def test_tag_bind(self):
        events = []
        item1 = self.tv.insert('', 'end', tags=['call'])
        item2 = self.tv.insert('', 'end', tags=['call'])
        self.tv.tag_bind('call', '<ButtonPress-1>',
            lambda evt: events.append(1))
        self.tv.tag_bind('call', '<ButtonRelease-1>',
            lambda evt: events.append(2))

        self.tv.pack()
        self.tv.wait_visibility()
        self.tv.update()

        pos_y = set()
        found = set()
        for i in range(0, 100, 10):
            if len(found) == 2: # item1 and item2 already found
                break
            item_id = self.tv.identify_row(i)
            if item_id and item_id not in found:
                pos_y.add(i)
                found.add(item_id)

        self.failUnlessEqual(len(pos_y), 2) # item1 and item2 y pos
        for y in pos_y:
            support.simulate_mouse_click(self.tv, 0, y)

        # by now there should be 4 things in the events list, since each
        # item had a bind for two events that were simulated above
        self.failUnlessEqual(len(events), 4)
        for evt in zip(events[::2], events[1::2]):
            self.failUnlessEqual(evt, (1, 2))


def test_main():
    support.run(TreeviewTest)

if __name__ == "__main__":
    test_main()
