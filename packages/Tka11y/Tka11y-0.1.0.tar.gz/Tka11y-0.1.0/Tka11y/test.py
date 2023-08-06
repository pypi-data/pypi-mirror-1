'''
Tests for Accessibility-aware Tkinter.

Author: Allen B. Taylor, a.b.taylor@gmail.com
'''

from Tka11y import *

def test():
    root = Tk()

    # Menus.
    def menuCommand(action):
        print 'Performing menu command:', action
    mainMenu = Menu(root, tearoff=False)
    fileMenu = Menu(root, tearoff=False)
    fileMenu.add_command(label='Open', underline=0,
        command = lambda action='open': menuCommand(action))
    fileMenu.add_command(label='Close', underline=0,
        command = lambda action='close': menuCommand(action))
    editMenu = Menu(root, tearoff=False)
    editMenu.add_command(label='Blah',
        command = lambda action='blah': menuCommand(action))
    editMenu.add_separator()
    editMenu.add_command(label='Blah2',
        command = lambda action='blah2': menuCommand(action))
    editMenu.add_separator()
    editMenu.add_command(label='Paste', underline=0,
        command = lambda action='paste': menuCommand(action))
    editMenu.insert_command(editMenu.index(END), label='Copy', underline=0,
        state=DISABLED, command = lambda action='copy': menuCommand(action))
    editMenu.add_separator()
    prefMenu = Menu(root, tearoff=False)
    prefMenu.add_command(label='User', underline=0,
        command = lambda action='user preferences': menuCommand(action))
    prefMenu.add_command(label='System', underline=0,
        command = lambda action='system preferences': menuCommand(action))
    prefMenu.add_checkbutton(label='Use System', underline=5,
        command = lambda action='user system preferences': menuCommand(action))
    editMenu.add_cascade(label='Preferences', underline=1, menu = prefMenu)
    editMenu.delete(0,3)

    mainMenu.add_cascade(label='Edit', underline=0, menu=editMenu)
    mainMenu.insert_cascade(0, label='File', underline=0, menu=fileMenu)
    root['menu'] = mainMenu

    # Popup menu.
    def popUpCommand():
        editMenu.post(root.winfo_rootx(), root.winfo_rooty())
    def popDownCommand():
        editMenu.unpost()
    popMenu = Menu(root)
    popMenu.add_command(label='Up', command=popUpCommand)
    popMenu.add_command(label='Down', command=popDownCommand)
    mainMenu.add_cascade(label='Pop', underline=0, menu=popMenu)

    # Label with Unicode (if supported).
    text = "This is Tcl/Tk version %s" % TclVersion
    text += " with Tka11y version %s" % Tka11yVersionString
    if TclVersion >= 8.1:
        try:
            text = text + unicode("\nThis should be a cedilla: \347",
                                  "iso-8859-1")
        except NameError:
            pass # no unicode support
    label = Label(root, text=text)
    label.pack()

    # Entry fields.
    entry = Entry(root)
    entry.insert(END, "Edit me!")
    entry.pack()
    entry2 = Entry(root,
        disabledbackground='red', disabledforeground='white')
    entry2.insert(END, "No, edit me!")
    entry2.configure(state=DISABLED)
    entry2.pack()
    password = Entry(root, show='*')
    password.pack()

    # Frame with some stuff inside.
    frame1 = Frame(root, borderwidth=2, relief=SUNKEN)
    frame1.pack(fill=X)
    frameLabel = Label(frame1,
        text='Disabled label in frame', state=DISABLED)
    frameLabel.pack()
    frameMessage = Message(frame1,
        text='Message in frame', fg='green', bg='white')
    frameMessage.pack()
    menuButton = Menubutton(frame1, text='Choose', underline=0)
    menuButton.pack(fill=X)
    menuButtonMenu = Menu(menuButton, tearoff=False)
    menuButtonMenu.add_command(label='Choice A', underline=7,
        command = lambda action='Choice A': menuCommand(action))
    menuButtonMenu.add_command(label='Choice B', underline=7,
        command = lambda action='Choice B': menuCommand(action))
    menuButton.config(menu=menuButtonMenu)

    # The classic changing button.
    button = Button(root, text="Click me!",
        command = lambda parent=root: parent.button.configure(
            text="[%s]" % parent.button['text']))
    button.pack()
    root.button = button

    button2 = Button(root,
        text='Do NOT click me', state=DISABLED, underline=3)
    button2.pack()

    # Frame for various buttons.
    frame2 = Frame(root, borderwidth=2, relief=SUNKEN)
    frame2.pack(fill=X)

    # Check button.
    checkbuttonValue = IntVar()
    checkbutton = Checkbutton(frame2,
        text='Toggle', variable=checkbuttonValue)
    checkbutton.pack(side=LEFT)
    checkbuttonLabel = Label(frame2, text=checkbuttonValue.get())
    checkbuttonLabel.pack(side=LEFT)
    checkbutton.config(command =
        lambda: checkbuttonLabel.config(text=checkbuttonValue.get()))

    # Radio buttons.
    radiobuttonValue = Variable()
    radiobuttonValue.set('-')
    radiobutton1 = Radiobutton(frame2, text='X',
        variable=radiobuttonValue, value='x')
    #print 'Assigning radiobutton 1 variable again'
    #radiobutton1['variable']=radiobuttonValue
    radiobutton1.pack(side=LEFT)
    radiobutton2 = Radiobutton(frame2, text='Y',
        variable=radiobuttonValue, value='y')
    radiobutton2.pack(side=LEFT)
    radiobutton3 = Radiobutton(frame2, text='Z',
        variable=radiobuttonValue, value='z')
    radiobutton3.pack(side=LEFT)
    radiobutton4 = Radiobutton(frame2, text='X2',
        variable=radiobuttonValue, value='x')
    radiobutton4.pack(side=LEFT)
    radiobuttonLabel = Label(frame2, text=radiobuttonValue.get())
    radiobuttonLabel.pack(side=LEFT)
    for radiobutton in [radiobutton1, radiobutton2, radiobutton3, radiobutton4]:
        radiobutton.config(command =
            lambda: radiobuttonLabel.config(text=radiobuttonValue.get()))

    # Option menu.
    optionMenuValue = Variable()
    optionMenu = OptionMenu(frame2, optionMenuValue, 'A', 'B', 'C')
    optionMenu.pack(side=RIGHT)

    # Listbox with insert and delete buttons.
    frame3 = Frame(root, borderwidth=2, relief=SUNKEN)
    frame3.pack(fill=X)
    listbox = Listbox(frame3, selectmode=EXTENDED)
    listbox.pack(side=LEFT, fill=Y)
    listScrollbar = Scrollbar(frame3, orient=VERTICAL)
    listScrollbar.pack(side=LEFT, fill=Y)
    listbox['yscrollcommand'] = listScrollbar.set
    listScrollbar['command'] = listbox.yview
    def insertListItem():
        if len(listbox.curselection()) > 0:
            listbox.insert(ACTIVE, listbox.size())
        else:
            listbox.insert(END, listbox.size())
    listboxInsertButton = Button(frame3,
        text='Insert', command=insertListItem)
    listboxInsertButton.pack()
    def deleteListItem():
        if listbox.size() > 0 and len(listbox.curselection()) > 0:
            newActive = listbox.index(ACTIVE)
            listbox.delete(ACTIVE)
            if listbox.size() > 0:
                if newActive >= listbox.size():
                    newActive -= 1
                listbox.selection_set(newActive)
    listboxDeleteButton = Button(frame3,
        text='Delete', command=deleteListItem)
    listboxDeleteButton.pack()
    def unselectListItem():
        if listbox.size() > 0:
            listbox.selection_clear(0, END)
    listboxUnselectButton = Button(frame3,
        text='Unselect', command=unselectListItem)
    listboxUnselectButton.pack()

    def toggleEnable():
        if listbox.cget('state') == DISABLED:
            listbox.config(state = NORMAL)
        else:
            listbox.config(state = DISABLED)
    listboxDisableButton = Button(frame3, text='Toggle enable',
        command=toggleEnable)
    listboxDisableButton.pack()

    listbox.insert(END, 'a', 'bb', 'ccc')
    listbox.insert(2, 'dddd', 'eeeee')

    frame4 = LabelFrame(root, borderwidth=2, relief=SUNKEN, text='Ups & downs')
    frame4.pack(fill=X)
    scale = Scale(frame4,
        label='Slide', from_=20, to=50, resolution=0.5, orient=HORIZONTAL)
    scale.pack()
    standaloneScrollbar = Scrollbar(frame4, orient=HORIZONTAL)
    standaloneScrollbar.pack(fill=X)
    standaloneScrollbar.set(0.25, 0.5)
    spinbox = Spinbox(frame4,
        from_=1, to=10, increment=0.5, justify=RIGHT)
    spinbox.pack()

    frame5 = LabelFrame(root,
        borderwidth=2, relief=SUNKEN, text='Edit')
    frame5.grid_rowconfigure(0, weight=1)
    frame5.grid_columnconfigure(0, weight=1)
    frame5.pack(fill=X)
    textVericalScrollbar = Scrollbar(frame5, orient=VERTICAL)
    textVericalScrollbar.grid(row=0, column=1, sticky=NS)
    textHorizontalScrollbar = Scrollbar(frame5, orient=HORIZONTAL)
    textHorizontalScrollbar.grid(row=1, column=0, sticky=EW)
    text = Text(frame5, height=5, wrap=NONE)
    text.grid(row=0, column=0, sticky=NSEW)
    text['yscrollcommand'] = textVericalScrollbar.set
    textVericalScrollbar['command'] = text.yview
    text['xscrollcommand'] = textHorizontalScrollbar.set
    textHorizontalScrollbar['command'] = text.xview
    text.tag_config('fg-green', foreground='green')
    text.tag_config('bg-blue', background='blue', foreground='orange')
    text.tag_config('fg-yellow', foreground='yellow')
    text.tag_config('ul', underline=1)
    text.insert(END,'We can ')
    text.insert(END,'put ', ('fg-green'))
    def sayHi():
        print 'Hi there'
    buttonInText = Button(text, text='Widget', command=sayHi)
    text.window_create(END, window=buttonInText)
    text.insert(END, 's ', ('fg-green'))
    text.insert(END, 'and', ('fg-green', 'bg-blue', 'fg-yellow'))
    text.insert(END, ' ', ('fg-green'))
    text.insert(END, 'images', ('bg-blue', 'fg-green'))
    text.insert(END, ' (')
    bitmapData = """
        #define im_width 32
        #define im_height 32
        static char im_bits[] = {
        0xaf,0x6d,0xeb,0xd6,0x55,0xdb,0xb6,0x2f,
        0xaf,0xaa,0x6a,0x6d,0x55,0x7b,0xd7,0x1b,
        0xad,0xd6,0xb5,0xae,0xad,0x55,0x6f,0x05,
        0xad,0xba,0xab,0xd6,0xaa,0xd5,0x5f,0x93,
        0xad,0x76,0x7d,0x67,0x5a,0xd5,0xd7,0xa3,
        0xad,0xbd,0xfe,0xea,0x5a,0xab,0x69,0xb3,
        0xad,0x55,0xde,0xd8,0x2e,0x2b,0xb5,0x6a,
        0x69,0x4b,0x3f,0xb4,0x9e,0x92,0xb5,0xed,
        0xd5,0xca,0x9c,0xb4,0x5a,0xa1,0x2a,0x6d,
        0xad,0x6c,0x5f,0xda,0x2c,0x91,0xbb,0xf6,
        0xad,0xaa,0x96,0xaa,0x5a,0xca,0x9d,0xfe,
        0x2c,0xa5,0x2a,0xd3,0x9a,0x8a,0x4f,0xfd,
        0x2c,0x25,0x4a,0x6b,0x4d,0x45,0x9f,0xba,
        0x1a,0xaa,0x7a,0xb5,0xaa,0x44,0x6b,0x5b,
        0x1a,0x55,0xfd,0x5e,0x4e,0xa2,0x6b,0x59,
        0x9a,0xa4,0xde,0x4a,0x4a,0xd2,0xf5,0xaa
        };
        """
    imageInText = BitmapImage(data=bitmapData,
        foreground='orange',background='blue')
    text.image_create(END, image=imageInText)
    text.insert(END, ') inside a ')
    text.insert(END, 'Text', ('ul'))
    text.insert(END, ' widget.')
    text.mark_set('a', '1.0')
    text.mark_set('b', '1.1')
    text.tag_add('b','1.3')

    # Quit button.
    quitButton = Button(root,
        text="Quit", underline=0, command=root.destroy)
    quitButton.pack()
    root.bind('<Alt-q>', lambda event: quitButton.invoke())

    # The following three commands are needed so the window pops
    # up on top on Windows...
    root.iconify()
    root.update()
    root.deiconify()

    root.mainloop()

    print 'Thanks for testing Tka11y.'

if __name__ == '__main__':
    test()
