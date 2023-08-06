import unittest
import tkinter
import ttk

import support

class WidgetTest(unittest.TestCase):
    """Tests methods available in every ttk widget."""

    def setUp(self):
        self.widget = ttk.Button()
        self.widget.pack()
        self.widget.wait_visibility()

    def tearDown(self):
        self.widget.destroy()


    def test_identify(self):
        self.widget.update_idletasks()
        self.failUnlessEqual(self.widget.identify(5, 5), "label")
        self.failUnlessEqual(self.widget.identify(-1, -1), "")

        self.failUnlessRaises(tkinter.TclError, self.widget.identify, None, 5)
        self.failUnlessRaises(tkinter.TclError, self.widget.identify, 5, None)
        self.failUnlessRaises(tkinter.TclError, self.widget.identify, 5, '')


    def test_widget_state(self):
        # XXX not sure about the portability of all these tests
        self.failUnlessEqual(self.widget.state(), ())
        self.failUnlessEqual(self.widget.instate(['!disabled']), True)

        # changing from !disabled to disabled
        self.failUnlessEqual(self.widget.state(['disabled']), ('!disabled', ))
        # no state change
        self.failUnlessEqual(self.widget.state(['disabled']), ())
        # change back to !disable but also active
        self.failUnlessEqual(self.widget.state(['!disabled', 'active']),
            ('!active', 'disabled'))
        # no state changes, again
        self.failUnlessEqual(self.widget.state(['!disabled', 'active']), ())
        self.failUnlessEqual(self.widget.state(['active', '!disabled']), ())

        def test_cb(arg1, **kw):
            return arg1, kw
        self.failUnlessEqual(self.widget.instate(['!disabled'],
            test_cb, "hi", **{"msg": "there"}),
            ('hi', {'msg': 'there'}))

        # attempt to set invalid statespec
        currstate = self.widget.state()
        self.failUnlessRaises(tkinter.TclError, self.widget.instate,
            ['badstate'])
        self.failUnlessRaises(tkinter.TclError, self.widget.instate,
            ['disabled', 'badstate'])
        # verify that widget didn't change its state
        self.failUnlessEqual(currstate, self.widget.state())

        # ensuring that passing None as state doesn't modify current state
        self.widget.state(['active', '!disabled'])
        self.failUnlessEqual(self.widget.state(), ('active', ))


class ButtonTest(unittest.TestCase):

    def test_invoke(self):
        success = []
        btn = ttk.Button(command=lambda: success.append(1))
        btn.invoke()
        self.failUnless(success)


class CheckbuttonTest(unittest.TestCase):

    def test_invoke(self):
        success = []
        def cb_test():
            success.append(1)
            return "cb test called"

        cbtn = ttk.Checkbutton(command=cb_test)
        # the variable automatically created by ttk.Checkbutton is actually
        # undefined till we invoke the Checkbutton
        self.failUnlessEqual(cbtn.state(), ('alternate', ))
        self.failUnlessRaises(tkinter.TclError, cbtn.tk.globalgetvar,
            cbtn['variable'])

        res = cbtn.invoke()
        self.failUnlessEqual(res, "cb test called")
        self.failUnlessEqual(cbtn['onvalue'],
            cbtn.tk.globalgetvar(cbtn['variable']))
        self.failUnless(success)

        cbtn['command'] = ''
        res = cbtn.invoke()
        self.failUnlessEqual(res, '')
        self.failIf(len(success) > 1)
        self.failUnlessEqual(cbtn['offvalue'],
            cbtn.tk.globalgetvar(cbtn['variable']))


class ComboboxTest(unittest.TestCase):

    def setUp(self):
        self.combo = ttk.Combobox()

    def tearDown(self):
        self.combo.destroy()

    def _show_drop_down_listbox(self):
        width = self.combo.winfo_width()
        self.combo.event_generate('<ButtonPress-1>', x=width - 5, y=5)
        self.combo.event_generate('<ButtonRelease-1>', x=width - 5, y=5)
        self.combo.update_idletasks()


    def test_virtual_event(self):
        success = []

        self.combo['values'] = [1]
        self.combo.bind('<<ComboboxSelected>>',
            lambda evt: success.append(True))
        self.combo.pack()
        self.combo.wait_visibility()

        height = self.combo.winfo_height()
        self._show_drop_down_listbox()
        self.combo.update()
        self.combo.event_generate('<Return>')
        self.combo.update()

        self.failUnless(success)


    def test_postcommand(self):
        success = []

        self.combo['postcommand'] = lambda: success.append(True)
        self.combo.pack()
        self.combo.wait_visibility()

        self._show_drop_down_listbox()
        self.failUnless(success)

        # testing postcommand removal
        self.combo['postcommand'] = ''
        self._show_drop_down_listbox()
        self.failUnlessEqual(len(success), 1)


    def test_values(self):
        def check_get_current(getval, currval):
            self.failUnlessEqual(self.combo.get(), getval)
            self.failUnlessEqual(self.combo.current(), currval)

        check_get_current('', -1)

        self.combo['values'] = ['a', 1, 'c']

        self.combo.set('c')
        check_get_current('c', 2)

        self.combo.current(0)
        check_get_current('a', 0)

        self.combo.set('d')
        check_get_current('d', -1)

        # testing values with empty string
        self.combo.set('')
        self.combo['values'] = (1, 2, '', 3)
        check_get_current('', 2)

        # testing values with empty string set through configure
        self.combo.configure(values=[1, '', 2])
        self.failUnlessEqual(self.combo['values'], ('1', '', '2'))

        # out of range
        self.failUnlessRaises(tkinter.TclError, self.combo.current,
            len(self.combo['values']))
        # it expects an integer (or something that can be converted to int)
        self.failUnlessRaises(tkinter.TclError, self.combo.current, '')

        # testing creating combobox with empty string in values
        combo2 = ttk.Combobox(values=[1, 2, ''])
        self.failUnlessEqual(combo2['values'], ('1', '2', ''))
        combo2.destroy()


class EntryTest(unittest.TestCase):

    def setUp(self):
        self.entry = ttk.Entry()

    def tearDown(self):
        self.entry.destroy()


    def test_bbox(self):
        self.failUnlessEqual(len(self.entry.bbox(0)), 4)
        for item in self.entry.bbox(0):
            self.failUnless(isinstance(item, int))

        self.failUnlessRaises(tkinter.TclError, self.entry.bbox, 'noindex')
        self.failUnlessRaises(tkinter.TclError, self.entry.bbox, None)


    def test_identify(self):
        self.entry.pack()
        self.entry.wait_visibility()
        self.entry.update_idletasks()

        self.failUnlessEqual(self.entry.identify(5, 5), "textarea")
        self.failUnlessEqual(self.entry.identify(-1, -1), "")

        self.failUnlessRaises(tkinter.TclError, self.entry.identify, None, 5)
        self.failUnlessRaises(tkinter.TclError, self.entry.identify, 5, None)
        self.failUnlessRaises(tkinter.TclError, self.entry.identify, 5, '')


    def test_validation_options(self):
        success = []
        test_invalid = lambda: success.append(True)

        self.entry['validate'] = 'none'
        self.entry['validatecommand'] = lambda: False

        self.entry['invalidcommand'] = test_invalid
        self.entry.validate()
        self.failUnless(success)

        self.entry['invalidcommand'] = ''
        self.entry.validate()
        self.failUnlessEqual(len(success), 1)

        self.entry['invalidcommand'] = test_invalid
        self.entry['validatecommand'] = lambda: True
        self.entry.validate()
        self.failUnlessEqual(len(success), 1)

        self.entry['validatecommand'] = ''
        self.entry.validate()
        self.failUnlessEqual(len(success), 1)

        self.entry['validatecommand'] = True
        self.failUnlessRaises(tkinter.TclError, self.entry.validate)


    def test_validation(self):
        validation = []
        def validate(to_insert):
            if not 'a' <= to_insert.lower() <= 'z':
                validation.append(False)
                return False
            validation.append(True)
            return True

        self.entry['validate'] = 'key'
        self.entry['validatecommand'] = self.entry.register(validate), '%S'

        self.entry.insert('end', 1)
        self.entry.insert('end', 'a')
        self.failUnlessEqual(validation, [False, True])
        self.failUnlessEqual(self.entry.get(), 'a')


    def test_revalidation(self):
        def validate(content):
            for letter in content:
                if not 'a' <= letter.lower() <= 'z':
                    return False
            return True

        self.entry['validatecommand'] = self.entry.register(validate), '%P'

        self.entry.insert('end', 'avocado')
        self.failUnlessEqual(self.entry.validate(), True)
        self.failUnlessEqual(self.entry.state(), ())

        self.entry.delete(0, 'end')
        self.failUnlessEqual(self.entry.get(), '')
        
        self.entry.insert('end', 'a1b')
        self.failUnlessEqual(self.entry.validate(), False)
        self.failUnlessEqual(self.entry.state(), ('invalid', ))

        self.entry.delete(1)
        self.failUnlessEqual(self.entry.validate(), True)
        self.failUnlessEqual(self.entry.state(), ())


class PanedwindowTest(unittest.TestCase):

    def setUp(self):
        self.paned = ttk.Panedwindow()

    def tearDown(self):
        self.paned.destroy()


    def test_add(self):
        # attempt to add a child that is not a direct child of the paned window
        label = ttk.Label(self.paned)
        child = ttk.Label(label)
        self.failUnlessRaises(tkinter.TclError, self.paned.add, child)
        label.destroy()
        child.destroy()
        # another attempt
        label = ttk.Label()
        child = ttk.Label(label)
        self.failUnlessRaises(tkinter.TclError, self.paned.add, child)
        child.destroy()
        label.destroy()

        good_child = ttk.Label()
        self.paned.add(good_child)
        # re-adding a child is not accepted
        self.failUnlessRaises(tkinter.TclError, self.paned.add, good_child)

        other_child = ttk.Label(self.paned)
        self.paned.add(other_child)
        self.failUnlessEqual(self.paned.pane(0), self.paned.pane(1))
        self.failUnlessRaises(tkinter.TclError, self.paned.pane, 2)
        good_child.destroy()
        other_child.destroy()
        self.failUnlessRaises(tkinter.TclError, self.paned.pane, 0)


    def test_forget(self):
        self.failUnlessRaises(tkinter.TclError, self.paned.forget, None)
        self.failUnlessRaises(tkinter.TclError, self.paned.forget, 0)

        self.paned.add(ttk.Label())
        self.paned.forget(0)
        self.failUnlessRaises(tkinter.TclError, self.paned.forget, 0)


    def test_insert(self):
        self.failUnlessRaises(tkinter.TclError, self.paned.insert, None, 0)
        self.failUnlessRaises(tkinter.TclError, self.paned.insert, 0, None)
        self.failUnlessRaises(tkinter.TclError, self.paned.insert, 0, 0)

        child = ttk.Label()
        child2 = ttk.Label()
        child3 = ttk.Label()

        self.failUnlessRaises(tkinter.TclError, self.paned.insert, 0, child)

        self.paned.insert('end', child2)
        self.paned.insert(0, child)
        self.failUnlessEqual(self.paned.panes(), (str(child), str(child2)))

        self.paned.insert(0, child2)
        self.failUnlessEqual(self.paned.panes(), (str(child2), str(child)))

        self.paned.insert('end', child3)
        self.failUnlessEqual(self.paned.panes(),
            (str(child2), str(child), str(child3)))

        # reinserting a child should move it to its current position
        panes = self.paned.panes()
        self.paned.insert('end', child3)
        self.failUnlessEqual(panes, self.paned.panes())

        # moving child3 to child2 position should result in child2 ending up
        # in previous child position and child ending up in previous child3
        # position
        self.paned.insert(child2, child3)
        self.failUnlessEqual(self.paned.panes(),
            (str(child3), str(child2), str(child)))


    def test_pane(self):
        self.failUnlessRaises(tkinter.TclError, self.paned.pane, 0)

        child = ttk.Label()
        self.paned.add(child)
        self.failUnless(isinstance(self.paned.pane(0), dict))
        self.failUnlessEqual(self.paned.pane(0, weight=None), 0)
        self.failUnlessEqual(self.paned.pane(0), self.paned.pane(str(child)))

        self.failUnlessRaises(tkinter.TclError, self.paned.pane, 0,
            badoption='somevalue')


    def test_sashpos(self):
        self.failUnlessRaises(tkinter.TclError, self.paned.sashpos, None)
        self.failUnlessRaises(tkinter.TclError, self.paned.sashpos, '')
        self.failUnlessRaises(tkinter.TclError, self.paned.sashpos, 0)

        child = ttk.Label(self.paned, text='a')
        self.paned.add(child, weight=1)
        self.failUnlessRaises(tkinter.TclError, self.paned.sashpos, 0)
        child2 = ttk.Label(self.paned, text='b')
        self.paned.add(child2)
        self.failUnlessRaises(tkinter.TclError, self.paned.sashpos, 1)

        self.paned.pack(expand=True, fill='both')
        self.paned.wait_visibility()

        curr_pos = self.paned.sashpos(0)
        self.paned.sashpos(0, 1000)
        self.failUnless(curr_pos != self.paned.sashpos(0))
        self.failUnless(isinstance(self.paned.sashpos(0), int))


class RadiobuttonTest(unittest.TestCase):

    def test_invoke(self):
        success = []
        def cb_test():
            success.append(1)
            return "cb test called"

        myvar = tkinter.IntVar()
        cbtn = ttk.Radiobutton(command=cb_test, variable=myvar, value=0)
        cbtn2 = ttk.Radiobutton(command=cb_test, variable=myvar, value=1)

        res = cbtn.invoke()
        self.failUnlessEqual(res, "cb test called")
        self.failUnlessEqual(cbtn['value'], myvar.get())
        self.failUnlessEqual(myvar.get(),
            cbtn.tk.globalgetvar(cbtn['variable']))
        self.failUnless(success)

        cbtn2['command'] = ''
        res = cbtn2.invoke()
        self.failUnlessEqual(res, '')
        self.failIf(len(success) > 1)
        self.failUnlessEqual(cbtn2['value'], myvar.get())
        self.failUnlessEqual(myvar.get(),
            cbtn.tk.globalgetvar(cbtn['variable']))

        self.failUnlessEqual(str(cbtn['variable']), str(cbtn2['variable']))



class ScaleTest(unittest.TestCase):

    def setUp(self):
        self.scale = ttk.Scale()
        self.scale.pack()
        self.scale.update()

    def tearDown(self):
        self.scale.destroy()


    def test_custom_event(self):
        failure = [1, 1, 1] # will need to be empty

        funcid = self.scale.bind('<<RangeChanged>>', lambda evt: failure.pop())

        self.scale['from'] = 10
        self.scale['from_'] = 10
        self.scale['to'] = 3

        self.failIf(failure)

        failure = [1, 1, 1]
        self.scale.configure(from_=2, to=5)
        self.scale.configure(from_=0, to=-2)
        self.scale.configure(to=10)

        self.failIf(failure)


    def test_get(self):
        scale_width = self.scale.winfo_width()
        self.failUnlessEqual(self.scale.get(scale_width, 0), self.scale['to'])

        self.failUnlessEqual(self.scale.get(0, 0), self.scale['from'])
        self.failUnlessEqual(self.scale.get(), self.scale['value'])
        self.scale['value'] = 30
        self.failUnlessEqual(self.scale.get(), self.scale['value'])

        self.failUnlessRaises(tkinter.TclError, self.scale.get, '', 0)
        self.failUnlessRaises(tkinter.TclError, self.scale.get, 0, '')


    def test_set(self):
        # set restricts the max/min values according to the current range
        max = self.scale['to']
        new_max = max + 10
        self.scale.set(new_max)
        self.failUnlessEqual(self.scale.get(), max)
        min = self.scale['from']
        self.scale.set(min - 1)
        self.failUnlessEqual(self.scale.get(), min)

        # changing directly the variable doesn't impose this limitation tho
        var = tkinter.DoubleVar()
        self.scale['variable'] = var
        var.set(max + 5)
        self.failUnlessEqual(self.scale.get(), var.get())
        self.failUnlessEqual(self.scale.get(), max + 5)
        del var

        # the same happens with the value option
        self.scale['value'] = max + 10
        self.failUnlessEqual(self.scale.get(), max + 10)
        self.failUnlessEqual(self.scale.get(), self.scale['value'])

        # nevertheless, note that the max/min values we can get specifying
        # x, y coords are the ones according to the current range
        self.failUnlessEqual(self.scale.get(0, 0), min)
        self.failUnlessEqual(self.scale.get(self.scale.winfo_width(), 0), max)

        self.failUnlessRaises(tkinter.TclError, self.scale.set, None)


def test_main():
    support.run(WidgetTest, ButtonTest, CheckbuttonTest, RadiobuttonTest,
        ComboboxTest, EntryTest, PanedwindowTest, ScaleTest)

if __name__ == "__main__":
    test_main()
