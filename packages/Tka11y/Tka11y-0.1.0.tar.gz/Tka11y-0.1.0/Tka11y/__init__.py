'''Accessibility-aware Tkinter.

This module makes it possible for accessibility clients (e.g., audible
readers, magnifiers, etc.) to get accessibility data (name, description,
role, actions, etc.) from the Tk widgets of Python applications that
use Tkinter. It also allows automated GUI application testers that use the
accessibility interface (such as dogtail, LDTP, and Accerciser) to control
the Tk widgets of these applications.

Currently, accessibility is only available via ATK <=> AT-SPI on Linux.
Sorry, no Windows MSAA support.

Usage:

    import Tka11y as Tkinter
    # Use "Tkinter." as usual.

or

    from Tka11y import *
    # Use Tkinter module definitions as usual.

This module modifies the original Tkinter module in memory, making all
Tk widgets accessibility-aware.

Note that, because it modifies the original Tkinter module (in memory),
other modules that use Tkinter (e.g., Pmw) reap the benefits automagically
as long as Tka11y is imported at some point before the first Tk object
is created.

Author: Allen B. Taylor, a.b.taylor@gmail.com
'''

from Tkinter import *
import Tkinter # to gain access to internal functions
import papi.atk as atk
import sys

###
### Externally accessible constants.
### Some of these may be modified by the user. See Tka11yConstants module for
### details.
###

import constants as Tka11yConstants

# Make version information easy to get at.
Tka11yVersion = Tka11yConstants.Version
Tka11yVersionString = Tka11yConstants.VersionString

###
### AT constants.
### These should be defined in Papi, but aren't (yet?).
###

# AccessibleCoordType enumeration.
_SPI_COORD_TYPE_SCREEN = 0
_SPI_COORD_TYPE_WINDOW = 1

# AccessibleComponentLayer enumeration.
_SPI_LAYER_INVALID = 0
_SPI_LAYER_BACKGROUND = 1
_SPI_LAYER_CANVAS = 2
_SPI_LAYER_WIDGET = 3
_SPI_LAYER_MDI = 4
_SPI_LAYER_POPUP = 5
_SPI_LAYER_OVERLAY = 6
_SPI_LAYER_WINDOW = 7

# AtkTextAttribute constants.
_ATK_TEXT_ATTR_UNDERLINE = atk.text_attribute_for_name('underline')
_ATK_TEXT_ATTR_BG_COLOR = atk.text_attribute_for_name('bg-color')
_ATK_TEXT_ATTR_FG_COLOR = atk.text_attribute_for_name('fg-color')
_ATK_TEXT_ATTR_INDICATOR_COLOR = atk.text_attribute_register('indicator-color')

###
### Application initialization.
###

# Publish accessible application. Note that accessibility clients won't see
# the information until the first Tk object is created and the ATK "iterate"
# pump starts.
_atkApp = atk.AtkObject()
_atkApp.name = sys.argv[0]
if len(_atkApp.name) == 0:
    _atkApp.name = 'Tkinter Application'
_atkApp.description = 'Tkinter Application'
_atkApp.role = atk.ATK_ROLE_APPLICATION
_atkApp._Tk_toplevels = []

_afterIterateId = 0

###
### Tk widget to ATK role mappings.
###

Misc._atk_role          = atk.ATK_ROLE_UNKNOWN
Tk._atk_role            = atk.ATK_ROLE_WINDOW
Toplevel._atk_role      = atk.ATK_ROLE_DIALOG
Button._atk_role        = atk.ATK_ROLE_PUSH_BUTTON
Canvas._atk_role        = atk.ATK_ROLE_CANVAS
Checkbutton._atk_role   = atk.ATK_ROLE_CHECK_BOX
Entry._atk_role         = atk.ATK_ROLE_ENTRY
Frame._atk_role         = atk.ATK_ROLE_PANEL
Label._atk_role         = atk.ATK_ROLE_LABEL
Listbox._atk_role       = atk.ATK_ROLE_LIST
Menu._atk_role          = atk.ATK_ROLE_MENU
try: # Menubutton is obsolete.
    Menubutton._atk_role= atk.ATK_ROLE_MENU
except:
    pass
try: # Message is obsolete.
    Message._atk_role   = atk.ATK_ROLE_LABEL
except:
    pass
Radiobutton._atk_role   = atk.ATK_ROLE_RADIO_BUTTON
Scale._atk_role         = atk.ATK_ROLE_SLIDER
Scrollbar._atk_role     = atk.ATK_ROLE_SCROLL_BAR
Text._atk_role          = atk.ATK_ROLE_TEXT
OptionMenu._atk_role    = atk.ATK_ROLE_COMBO_BOX
try: # Spinbox in new in Tk 8.4
    Spinbox._atk_role   = atk.ATK_ROLE_SPIN_BUTTON
except:
    pass
LabelFrame._atk_role    = atk.ATK_ROLE_PANEL
PanedWindow._atk_role   = atk.ATK_ROLE_SPLIT_PANE

_atkMenuContentRoles = (
    atk.ATK_ROLE_MENU, atk.ATK_ROLE_MENU_ITEM,
    atk.ATK_ROLE_TEAR_OFF_MENU_ITEM,
    atk.ATK_ROLE_CHECK_MENU_ITEM,
    atk.ATK_ROLE_RADIO_MENU_ITEM,
    )

# Define a central variable database.
class _VarDB:

    def __init__(self):

        # Define a variable database with the following format:
        #  {varName: {(widget, configKey): None, ...}, ...}
        # where:
        # - widget is either a widget object or, for menu items, a tuple of
        #   parent menu widget and item accessible.
        # - configKey is typically one of 'variable', 'textvariable', etc.
        self.vars = {}

        # Define a cross reference map of widgets to variables with format:
        #  {widget: {varName: configKey, ...}, ...}
        # where:
        # - widget is either a widget object or, for menu items, a tuple of
        #   parent menu widget and item accessible.
        self.widgets = {}

    def add(self, var, widget, configKey):

        varId = str(var)

        # If variable tracing is not on for this variable, it is because there
        # is no Variable instance for the variable. Therefore, create one.
        if varId not in Variable._atk_varTraces:
            Variable._atk_tclVars.append(Variable(name = varId))

        if varId not in self.vars:
            self.vars[varId] = {}
        self.vars[varId][widget, configKey] = None
        if widget not in self.widgets:
            self.widgets[widget] = {}
        self.widgets[widget][varId] = configKey

        # Perform an update after associating a new widget.
        Variable._atk_vars.update(varId)

    def remove(self, var, widget, configKey):

        varId = str(var)

        del self.vars[varId][widget, configKey]
        if len(self.vars[varId]) == 0:
            del self.vars[varId]
        del self.widgets[widget][varId]
        if len(self.widgets[widget]) == 0:
            del self.widgets[widget]

    def __contains__(self, var):
        varId = str(var)
        return varId in self.vars

    def update(self, var):

        varId = str(var)

        for widget, configKey in self.vars[varId].iterkeys():
            if isinstance(widget, tuple):
                widget, atkEntryObj = widget
                index = atkEntryObj.index_in_parent
                variable = widget.entrycget(index, configKey)
                if configKey == 'variable':
                    if widget.widgetName == 'menu':
                        menuType = widget.type(index)
                        if menuType == 'checkbutton':
                            atkEntryObj.SetState(atk.ATK_STATE_CHECKED,
                                unicode(widget.getvar(variable)) ==
                                unicode(widget.entrycget(index, 'onvalue')))
                        elif menuType == 'radiobutton':
                            atkEntryObj.SetState(atk.ATK_STATE_CHECKED,
                                unicode(widget.getvar(variable)) ==
                                unicode(widget.entrycget(index, 'value')))
            else:
                #atkObj = widget.__atkObj
                # The above line causes an attribute error to occur
                # (looking for an attribute named _VarDB__atkObj instead of
                # simply __atkObj), so the following line is used instead.
                atkObj = widget.__dict__['__atkObj']
                variable = widget[configKey]
                if configKey == 'variable':
                    if widget.widgetName == 'checkbutton':
                        atkObj.SetState(atk.ATK_STATE_CHECKED,
                            unicode(widget.getvar(variable)) ==
                            unicode(widget['onvalue']))
                    elif widget.widgetName == 'radiobutton':
                        atkObj.SetState(atk.ATK_STATE_CHECKED,
                            unicode(widget.getvar(variable)) ==
                            unicode(widget['value']))
                elif configKey == 'textvariable':
                    # Value of 'textvariable' variable overrides text value.
                    if 'name_config' in atkObj.__dict__ and \
                        atkObj.name_config == 'text':
                        name = unicode(widget.getvar(variable))
                        atkObj.name = name.encode('utf-8')
                elif configKey == 'listvariable':
                    if widget.widgetName == 'listbox':
                        # Reconstruct the list contents. Note that this is
                        # not done in the case that the variable was updated
                        # as a result of an append, insert, or delete. In
                        # these cases, the list is updated in a more efficient
                        # manner.
                        if '_bypassVariableUpdate' not in atkObj.__dict__:
                            for i in range(atkObj.n_accessible_children):
                                atkObj.ref_accessible_child(0).parent = None
                            for item in widget.getvar(variable):
                                _Listbox_appendItem(widget, item)

    def containsWidget(self, widget):
        return widget in self.widgets

    def removeWidget(self, widget):
        for varId, configKey in self.widgets[widget].iteritems():
            del self.vars[varId][widget, configKey]
            if len(self.vars[varId]) == 0:
                del self.vars[varId]
        del self.widgets[widget]

Variable._atk_vars = _VarDB()

# Define a list of implicit variables. These are variables that are created in
# Tcl but for some reason, do not have any corresponding Variable instance.
# For example, when creating a Checkbutton, if a variable is not specified,
# the Checkbutton still has a variable, but it is only known in Tcl. When
# this happens, we create a Variable instance (causing tracing to start) and
# then put a reference to it in this list.
Variable._atk_tclVars = []

###
### Variable hooks.
###

# Variable trace database with the following format:
#  {variableName: [traceName, refCount], ...}
Variable._atk_varTraces = {}

# Define a hook for class Variable's __init__ method.
def _Variable__init__(self, *args, **kwargs):

    Variable.__original__init__Tka11y(self, *args, **kwargs)

    # Trace updates to the variable so we can update the state of affected
    # widgets.
    varId = str(self)
    if varId in Variable._atk_varTraces:
        # The variable name has been previously used.
        Variable._atk_varTraces[varId][1] += 1
    else:
        # Start tracing updates to the variable.
        Variable._atk_varTraces[varId] = \
            [self.trace_variable('w', _Variable_update), 1]

Variable.__original__init__Tka11y = Variable.__init__
Variable.__init__ = _Variable__init__

# Define a hook for class Variable's __del__ method.
def _Variable__del__(self, *args, **kwargs):

    # End tracing. At program termination, the supporting data structures
    # may have already been cleaned up, so just ignore any exceptions here.
    try:
        varId = str(self)
        Variable._atk_varTraces[varId][1] -= 1
        if Variable._atk_varTraces[varId][1] == 0:
            self.trace_vdelete('w', Variable._atk_varTraces[varId][0])
            del Variable._atk_varTraces[varId]
    except:
        pass

    Variable.__original__del__Tka11y(self, *args, **kwargs)

Variable.__original__del__Tka11y = Variable.__del__
Variable.__del__ = _Variable__del__

# Define the variable trace call back function.
def _Variable_update(varId, index, mode):
    if varId in Variable._atk_vars:
        Variable._atk_vars.update(varId)

###
### Widget (and widget item) configuration.
###

def _Configure(widget, isConfig, getConfig, atkObj):
    """
    General-purpose configuration function used during object creation and
    subsequent configuration.

    Arguments:
    - widget:
        The widget begin configured, or in the case of a list item or menu
        entry, a tuple of (widget, index).
    - isConfig:
        A function called like isConfig(configKey). It returns True if
        configKey is being configured.
    - getConfig:
        A function called like getConfig(configKey). It returns the value
        being configured for configKey.
    - atkObj:
        The applicable accessibility object.
    """

    # Identify the type of object. For objects that are not widgets, special
    # names are constructed, e.g., 'Listbox-item', 'Menu-cascade', etc.
    if isinstance(widget, tuple):
        parentWidget, index = widget
        parentClass = parentWidget.__class__.__name__
        if parentClass == 'Menu':
            widgetClass = '%s-%s' % (parentClass, parentWidget.type(index))
        else:
            widgetClass = '%s-%s' % (parentClass, 'item')
    else:
        parentWidget = None
        widgetClass = widget.__class__.__name__

    # Handle name changes.
    if 'name_config' in atkObj.__dict__ and isConfig(atkObj.name_config):
        atkObj.name = unicode(getConfig(atkObj.name_config)).encode('utf-8')

    # Enable/disable.
    enabled = not isConfig('state') or getConfig('state') in (NORMAL, ACTIVE)
    atkObj.SetState(atk.ATK_STATE_ENABLED, enabled)

    # Set sensitivity to user interaction.
    sensitive = \
        enabled and \
        widgetClass not in ('Label', 'Message', 'Menu-separator')
    atkObj.SetState(atk.ATK_STATE_SENSITIVE, sensitive)

    # Set keyboard focusability.
    if isConfig('takefocus'):
        focusable = getConfig('takefocus') != '0'
        atkObj.SetState(atk.ATK_STATE_FOCUSABLE, focusable)

    # Set orientation.
    if isConfig('orient'):
        horizontal = getConfig('orient') == HORIZONTAL
        atkObj.SetState(atk.ATK_STATE_HORIZONTAL, horizontal)
        atkObj.SetState(atk.ATK_STATE_VERTICAL, not horizontal)

    # Check for password vs. regular text entry.
    if isConfig('show') and widgetClass == 'Entry':
        if getConfig('show') == '':
            atkObj.role = atk.ATK_ROLE_ENTRY
        else:
            atkObj.role = atk.ATK_ROLE_PASSWORD_TEXT

    # Check for listbox select mode change.
    if isConfig('selectmode') and widgetClass == 'Listbox':
        selectMode = getConfig('selectmode')
        atkObj.SetState(atk.ATK_STATE_MULTISELECTABLE,
            selectMode == MULTIPLE or selectMode == EXTENDED)

    # Handle adding new variable.
    for key in 'variable', 'textvariable', 'listvariable':
        if isConfig(key):
            newVar = getConfig(key)
            if newVar:
                if isinstance(widget, tuple):
                    Variable._atk_vars.add(newVar, (parentWidget, atkObj), key)
                else:
                    Variable._atk_vars.add(newVar, widget, key)

    # Handle adding new menu. Note that any previously assigned menu will have
    # been removed in _Deconfigure.
    if isConfig('menu'):
        newMenu = getConfig('menu')
        if newMenu != None and newMenu != '':
            if isinstance(newMenu, str):
                if isinstance(widget, tuple):
                    newMenu = parentWidget.nametowidget(newMenu)
                else:
                    newMenu = widget.nametowidget(newMenu)
            if atkObj.role in (atk.ATK_ROLE_MENU, atk.ATK_ROLE_COMBO_BOX):
                # Make menu items direct children of the menu's parent rather
                # than keeping a redundant menu level.
                for i in range(newMenu.__atkObj.n_accessible_children):
                    atkEntryObj = newMenu.__atkObj.ref_accessible_child(0)
                    atkEntryObj.parent = atkObj
                newMenu.__original_atkObj = newMenu.__atkObj
                newMenu.__atkObj = atkObj
            else:
                if widgetClass in ('Tk', 'Toplevel'):
                    newMenu.__atkObj.role = atk.ATK_ROLE_MENU_BAR
                    newMenu.__atkObj.description = 'menu bar'
                newMenu.__atkObj.parent = atkObj

def _Deconfigure(widget, isConfig, getConfig, atkObj):
    """
    General-purpose deconfiguration function used during object reconfiguration.

    Arguments: See _Configure, above.
    """

    # Identify the type of object. For objects that are not widgets, special
    # names are constructed, e.g., 'Listbox-item', 'Menu-cascade', etc.
    if isinstance(widget, tuple):
        parentWidget, index = widget
        parentClass = parentWidget.__class__.__name__
        if parentClass == 'Menu':
            widgetClass = '%s-%s' % (parentClass, parentWidget.type(index))
        else:
            widgetClass = '%s-%s' % (parentClass, 'item')
    else:
        parentWidget = None
        widgetClass = widget.__class__.__name__

    # Handle releasing old variable.
    for key in 'variable', 'textvariable', 'listvariable':
        if isConfig(key):
            oldVar = getConfig(key)
            if oldVar and oldVar in Variable._atk_vars:
                if isinstance(widget, tuple):
                    Variable._atk_vars.remove \
                        (oldVar, (parentWidget, atkObj), key)
                else:
                    Variable._atk_vars.remove(oldVar, widget, key)

    # Handle releasing old menu.
    if isConfig('menu'):
        try:
            oldMenu = getConfig('menu')
            if oldMenu != '':
                if not isinstance(oldMenu, Menu):
                    if isinstance(widget, tuple):
                        oldMenu = parentWidget.nametowidget(oldMenu)
                    else:
                        oldMenu = widget.nametowidget(oldMenu)
                if '__original_atkObj' in oldMenu.__dict__:
                    extractIndex = 0
                    for i in range(oldMenu.__atkObj.n_accessible_children):
                        child = \
                            oldMenu.__atkObj.ref_accessible_child(extractIndex)
                        if child.role in _atkMenuContentRoles:
                            child.parent = oldMenu.__original_atkObj
                        else:
                            extractIndex += 1
                    oldMenu.__atkObj = oldMenu.__original_atkObj
                    del oldMenu.__original_atkObj
                oldMenu.__atkObj.parent = None
        except:
            pass

###
### Widget actions.
###

# Constants.
_clickSequences = [
    '<Button-1>',
    '<ButtonPress-1>',
    '<ButtonRelease-1>',
    ]
_doubleClickSequences = [
    '<Double-Button-1>',
    '<Double-ButtonPress-1>',
    '<Double-ButtonRelease-1>',
    ]

# A collection of tags, each with an associated list of bind sequences (in
# canonical form).
_taggedSequences = {}

# General-purpose click action for clicking a widget.
def _Click(widget, clickCount):
    widget.event_generate('<Enter>')
    widget.event_generate('<Motion>', x=0, y=0)
    for i in range(clickCount):
        widget.event_generate('<Button-1>', x=0, y=0)
        widget.event_generate('<ButtonRelease-1>', x=0, y=0)
    widget.event_generate('<Leave>')
    return True

# Specialized click action for list box items.
def _ClickListBoxItem(listbox, atkItemObj, clickCount):
    index = atkItemObj.index_in_parent
    listbox.see(index)
    (x, y, width, height) = listbox.bbox(index)
    listbox.event_generate('<Enter>')
    listbox.event_generate('<Motion>', x=x, y=y)
    for i in range(clickCount):
        listbox.event_generate('<Button-1>', x=x, y=y)
        listbox.event_generate('<ButtonRelease-1>', x=x, y=y)
    listbox.event_generate('<Leave>')
    return True

# Add actions to a widget based on a bound event sequence.
# Note the sequence must be in canonical form (e.g., '<Button-1>', not '<1>').
def _AddBindAction(widget, sequence):
    if sequence in _clickSequences + _doubleClickSequences:
        if widget.__class__.__name__ == 'Listbox':
            for i in range(widget.__atkObj.n_accessible_children):
                atkItemObj = widget.__atkObj.ref_accessible_child(i)
                if sequence in _clickSequences:
                    atkItemObj.AddAction(
                        'click',
                        func=lambda atkItemObj=atkItemObj:
                            _ClickListBoxItem(widget, atkItemObj, 1))
                if sequence in _doubleClickSequences:
                    atkItemObj.AddAction(
                        'double-click',
                        func=lambda atkItemObj=atkItemObj:
                            _ClickListBoxItem(widget, atkItemObj, 2))
        else:
            if sequence in _clickSequences:
                widget.__atkObj.AddAction(
                    'click',
                    func=lambda: _Click(widget, 1))
            if sequence in _doubleClickSequences:
                widget.__atkObj.AddAction(
                    'double-click',
                    func=lambda: _Click(widget, 2))

###
### class Misc hooks.
###

# Add a method to class Misc to create or gain access to an existing
# accessibility object.
def _Misc_atk_object(self):
    if '__atkObj' not in self.__dict__:
        self.__atkObj = _AtkObject(self._atk_ifaces())
        self.__atkObj.role = self._atk_role

Misc._atk_object = _Misc_atk_object

# Add an interfaces query method to class Misc.
def _Misc_atk_ifaces(self):
    return atk.ATK_IFACE_COMPONENT | atk.ATK_IFACE_ACTION

Misc._atk_ifaces = _Misc_atk_ifaces

# Define an initialization method for class Misc. Note that class Misc doesn't
# have an __init__ method that any other class calls, so this method is called
# from the hook code defined for the other classes.
def _Misc_init(misc):

    # Define component interface methods...

    def get_extents(coord_type):
        return \
            misc.__atkObj.component_get_position(coord_type) + \
            misc.__atkObj.component_get_size(coord_type)
    misc.__atkObj.component_get_extents = get_extents

    def get_position(coord_type):
        x = misc.winfo_rootx()
        y = misc.winfo_rooty()
        if coord_type == _SPI_COORD_TYPE_SCREEN:
            return x, y
        else:
            return \
               x - misc.winfo_toplevel().winfo_rootx(), \
               y - misc.winfo_toplevel().winfo_rooty()
    misc.__atkObj.component_get_position = get_position

    def get_size(coord_type):
            return misc.winfo_width(), misc.winfo_height()
    misc.__atkObj.component_get_size = get_size

    misc.__atkObj.component_get_layer = lambda: _SPI_LAYER_WIDGET

    def grab_focus():
        misc.focus_force()
        return True
    misc.__atkObj.component_grab_focus = grab_focus

    # Actions are added via to calls to bind and bindtags.

# Define a hook for class Misc's destroy method.
def _Misc_destroy(self, *args, **kwargs):

    # Handle destruction of the widget, ignoring any expections thrown.
    # This ensures that problems don't interfere with its ultimate destruction.
    try:

        # Detach from parent.
        self.__atkObj.parent = None

        # Handle releasing any variables.
        if Variable._atk_vars.containsWidget(self):
            Variable._atk_vars.removeWidget(self)

        # Deal with destruction of a toplevel.
        if self.master == None:
            _atkApp._Tk_toplevels.remove(self)
            global _afterIterateId
            self.after_cancel(_afterIterateId)
            if len(_atkApp._Tk_toplevels) == 0:
                if Tka11yConstants.Debug >= 1:
                    print 'Shutting down ATK'
                atk.shutdown()
                if Tka11yConstants.Debug >= 1:
                    print 'ATK shut down'
            else:
                # Pass the iteration torch to another toplevel.
                newToplevel = _atkApp._Tk_toplevels[0]
                _afterIterateId = \
                    newToplevel.after_idle(_Atk_iterate, newToplevel)

        del self.__atkObj

    except:
        pass

    Misc.__original_destroy_Tka11y(self, *args, **kwargs)

Misc.__original_destroy_Tka11y = Misc.destroy
Misc.destroy = _Misc_destroy

# Define a hook for class Misc's configure method.
def _Misc_configure(self, cnf = None, **kwargs):

    configs = {}
    if kwargs:
        configs = Tkinter._cnfmerge((cnf, kwargs))
    elif cnf:
        configs = Tkinter._cnfmerge(cnf)

    if len(configs) > 0:
        _Deconfigure(
            self,
            lambda config: config in configs,
            self.cget,
            self.__atkObj)

    result = Misc.__original_configure_Tka11y(self, cnf, **kwargs)

    if len(configs) > 0:
        _Configure(
            self,
            lambda config: config in configs,
            self.cget,
            self.__atkObj)

    return result

Misc.__original_configure_Tka11y = Misc.configure
Misc.configure = _Misc_configure
Misc.config = _Misc_configure

# Implementation note for hooks for bindtags, bind, bind_class, etc.:
# Event sequences can be expressed in several ways. For example, a mouse click
# can be expressed as either '<Button-1>' or '<1>'. Because of this, the
# user-supplied sequence argument cannot be used if we want consistency.
# Therefore, each of the following routines uses a method to obtain the
# canonical name of the sequence(s) being added/removed. This method entails
# querying the bindings before and after calling the original method, and
# then taking the set difference between the two lists. This method yields
# the sequence(s) added/removed (depending on which set difference is done)
# in canonical form.

# Define a hook for class Misc's bindtags method.
def _Misc_bindtags(self, tagList=None):

    if tagList != None:
        bindtagsBefore = set(self.bindtags())

    result = Misc.__original_bindtags_Tka11y(self, tagList)
    if tagList == None:
        return result

    bindtagsAfter = set(self.bindtags())
    addedBindtags = list(bindtagsAfter - bindtagsBefore)

    for tag in addedBindtags:
        for sequence in _taggedSequences[tag]:
            _AddBindAction(self, sequence)

    return result

Misc.__original_bindtags_Tka11y = Misc.bindtags
Misc.bindtags = _Misc_bindtags

# Define a hook for class Misc's bind method.
def _Misc_bind(self, sequence=None, func=None, add=None):

    if sequence != None and func != None:
        bindSeqBefore = set(self.bind())

    result = Misc.__original_bind_Tka11y(self, sequence, func, add)
    if sequence == None or func == None:
        return result

    bindSeqAfter = set(self.bind())
    newSeqSet = bindSeqAfter - bindSeqBefore
    if len(newSeqSet) > 0:
        newSequence = tuple(newSeqSet)[0]
        _AddBindAction(self, newSequence)

    return result

Misc.__original_bind_Tka11y = Misc.bind
Misc.bind = _Misc_bind

# Define a hook for class Misc's bind_class method.
def _Misc_bind_class(self, className, sequence=None, func=None, add=None):

    if sequence != None and func != None:
        bindSeqBefore = set(self.bind_class(className))

    result = Misc.__original_bind_class_Tka11y \
        (self, className, sequence, func, add)
    if sequence == None or func == None:
        return result

    bindSeqAfter = set(self.bind_class(className))
    newSeqSet = bindSeqAfter - bindSeqBefore
    if len(newSeqSet) > 0:
        newSequence = tuple(newSeqSet)[0]
        if className not in _taggedSequences:
            _taggedSequences[className] = []
        _taggedSequences[className].append(newSequence)

    return result

Misc.__original_bind_class_Tka11y = Misc.bind_class
Misc.bind_class = _Misc_bind_class

# Define a hook for class Misc's unbind_class method.
def _Misc_unbind_class(self, className, sequence):

    bindSeqBefore = set(self.bind_class(className))

    Misc.__original_unbind_class_Tka11y(self, className, sequence)

    bindSeqAfter = set(self.bind_class(className))
    oldSeqSet = bindSeqBefore - bindSeqAfter
    if len(oldSequence) > 0:
        oldSequence = (tuple(oldSeqSet))[0]
        if className in _taggedSequences and \
            oldSequence in _taggedSequences[className]:
            _taggedSequences[className].remove(oldSequence)

Misc.__original_unbind_class_Tka11y = Misc.unbind_class
Misc.unbind_class = _Misc_unbind_class

###
### class Wm hooks.
###

# Add an interfaces query method to class Wm.
def _Wm_atk_ifaces(self):
    return atk.ATK_IFACE_ACTION
Wm._atk_ifaces = _Wm_atk_ifaces

# Define a hook for class Wm's wm_title method.
def _Wm_title(self, string = None):

    result = Wm.__original_title_Tka11y(self, string)
    if string == None:
        return result

    self.__atkObj.name = \
        Wm.__original_title_Tka11y(self).encode('utf-8')

    return result

Wm.__original_title_Tka11y = Wm.wm_title
Wm.wm_title = _Wm_title
Wm.title = _Wm_title

###
### class Tk hooks.
###

# Add an interfaces query method to class Tk.
def _Tk_atk_ifaces(self):
    return Wm._atk_ifaces(self) | Misc._atk_ifaces(self)
Tk._atk_ifaces = _Tk_atk_ifaces

# Define a hook for class Tk's __init__ method.
def _Tk__init__(self, *args, **kwargs):

    # Publish accessibility.
    self._atk_object()

    # Call the original __init__ method.
    Tk.__original__init__Tka11y(self, *args, **kwargs)

    self.__atkObj.name = self.wm_title().encode('utf-8')
    self.__atkObj.description = 'Tk toplevel window'
    self.__atkObj.parent = _atkApp
    self.__atkObj.SetState(atk.ATK_STATE_RESIZABLE)

    _Misc_init(self)

    # Start iteration processing for first toplevel.
    if len(_atkApp._Tk_toplevels) == 0:
        if Tka11yConstants.Debug >= 1:
            print 'Initializing ATK'
        atk.set_module_path(Tka11yConstants.AtkBridgePath)
        atk.set_root(_atkApp)
        atk.init()
        global _afterIterateId
        _afterIterateId = self.after_idle(_Atk_iterate, self)
    _atkApp._Tk_toplevels.append(self)

    _Configure(
        self,
        lambda config: config in self.keys(),
        self.cget,
        self.__atkObj)

    self.__atkObj.component_get_layer = lambda: _SPI_LAYER_WINDOW

    def maximize():
        try:
            self.state('zoomed')
        except:
            # Tk doesn't provide a way to maximize the window, so this is the
            # best we can do. Unfortunately, the 'restore' action will not
            # restore to the previous size in this case.
            self.wm_geometry('%dx%d+0+0' % self.maxsize())

    self.__atkObj.AddAction('close', func=self.destroy)
    self.__atkObj.AddAction('maximize', func=maximize)
    self.__atkObj.AddAction('minimize', func=self.wm_iconify)
    self.__atkObj.AddAction('restore', func=self.wm_deiconify)

Tk.__original__init__Tka11y = Tk.__init__
Tk.__init__ = _Tk__init__

###
### class BaseWidget hooks.
###

# Add an interfaces query method to class BaseWidget.
def _BaseWidget_atk_ifaces(self):
    return Misc._atk_ifaces(self) | 0
BaseWidget._atk_ifaces = _BaseWidget_atk_ifaces

# Default configuration value cache.
_defaultConfigCache = {}

# Hook for class BaseWidget's __init__ method.
def _BaseWidget__init__(self, master, widgetName, cnf={}, kw={}, extra=()):

    self._atk_object()

    configs = {}
    if kw:
        configs = Tkinter._cnfmerge((cnf, kw))
    elif cnf:
        configs = Tkinter._cnfmerge(cnf)

    # Prepare to cache default text attribute values for each unique
    # class/attribute pair. This is done upon the creation of the first of
    # each unique type of widget. If this widget is being created with
    # non-default text attributes, application of those attributes is deferred
    # until we can obtain those attributes' default values, after which the
    # attributes are applied, below.
    deferredConfigs = {}
    cacheKeys = []
    for configName in _textAttributeConfigKeys.keys():
        defaultConfigKey = (self.__class__, configName)
        if defaultConfigKey not in _defaultConfigCache:
            cacheKeys.append(defaultConfigKey)
            for configNameAlias in _AttributeConfigNameAliases(configName):
                if configNameAlias in configs:
                    deferredConfigs[configNameAlias] = configs[configNameAlias]
                    if configNameAlias in cnf:
                        del cnf[configNameAlias]
                    if configNameAlias in kw:
                        del kw[configNameAlias]

    # Call the original initialization routine, possibly without some keyword
    # parameters. These will be applied below, after their default values have
    # been cached.
    BaseWidget.__original__init__Tka11y \
        (self, master, widgetName, cnf, kw, extra)

    # Cache any default text attribute values identified above.
    for defaultConfigKey in cacheKeys:
        klass, configName = defaultConfigKey
        attribId, formatFunc = _textAttributeConfigKeys[configName]
        defaultValue = formatFunc(
            self,
            lambda config: config in self.keys(),
            lambda config, index: self.cget(config),
            configName, -1)
        _defaultConfigCache[defaultConfigKey] = defaultValue

    # Apply any deferred configuration items now that default text attribute
    # values have been cached.
    for configName, value in deferredConfigs.iteritems():
        self[configName] = value

    # Start iteration processing for first toplevel.
    if self.master == None:
        if len(_atkApp._Tk_toplevels) == 0:
            if Tka11yConstants.Debug >= 1:
                print 'Initializing ATK'
            atk.set_module_path(Tka11yConstants.AtkBridgePath)
            atk.set_root(_atkApp)
            atk.init()
            global _afterIterateId
            _afterIterateId = self.after_idle(_Atk_iterate, self)
        _atkApp._Tk_toplevels.append(self)

    # Try to find an appropriate configuration item to name the widget with
    # if it doesn't already have a fixed name. The name will be assigned
    # when the widget is configured, below.
    if self.__atkObj.name == None and \
        'name_config' not in self.__atkObj.__dict__:
        if 'label' in configs:
            self.__atkObj.name_config = 'label'
        elif 'text' in configs or 'textvariable' in configs:
            self.__atkObj.name_config = 'text'

    # If the widget doesn't already have a description, assign its widget name.
    if self.__atkObj.description == None:
        self.__atkObj.description = widgetName

    # Assign the parent.
    if self.__atkObj.parent == None:
        if self.master:
            self.__atkObj.parent = self.master.__atkObj
        else:
            self.__atkObj.parent = _atkApp

    # Define text interface methods if appropriate.
    if self._atk_ifaces() & atk.ATK_IFACE_TEXT:

        textConfig = None
        if 'label' in self.keys():
            textConfig = 'label'
        #elif 'text' in self.keys():
        else:
            textConfig = 'text'

        def get_text_character_count():
            return len(unicode(self[textConfig]))
        self.__atkObj.text_get_character_count = get_text_character_count

        def get_text(start, end):
            if end < 0: end = None
            return unicode(self[textConfig])[start:end].encode('utf-8')
        self.__atkObj.text_get_text = get_text

        self.__atkObj.text_get_character_at_offset = \
            lambda offset: self.__atkObj.text_get_text(offset, offset + 1)

        def isConfig(config):
            # For some strange reason, the call to keys() occasionally fails
            # on the first attempt with 'TypeError: an integer is required',
            # but a second invocation succeeds. This happens, for example,
            # when an AT client inserts text into an Entry widget and then
            # queries the text attributes immediately afterward.
            try:
                return config in self.keys()
            except:
                return config in self.keys()

        def getTextAttribute(configName, index=-1):
            return _GetTextAttribute(
                self,
                isConfig,
                lambda config, index: self.cget(config),
                configName, index)
        self.__atkObj._tkGetTextAttribute = getTextAttribute

        self.__atkObj.text_get_default_attributes = \
            lambda: _GetDefaultTextAttributes(self.__atkObj)

        self.__atkObj.text_get_run_attributes = \
            lambda offset: _GetTextRunAttributes(self.__atkObj, offset)

    _Misc_init(self)

    _Configure(
        self,
        lambda config: config in self.keys(),
        self.cget,
        self.__atkObj)

BaseWidget.__original__init__Tka11y = BaseWidget.__init__
BaseWidget.__init__ = _BaseWidget__init__

# Hook for class BaseWidget's destroy method.
def _BaseWidget_destroy(self):

    _BaseWidget_DeconfigureDeep(self)

    BaseWidget.__original_destroy_Tka11y(self)

BaseWidget.__original_destroy_Tka11y = BaseWidget.destroy
BaseWidget.destroy = _BaseWidget_destroy

def _BaseWidget_DeconfigureDeep(self):

    # Deconfigure children in depth first order.
    for c in self.children.values():
        _BaseWidget_DeconfigureDeep(c)

    # Deconfigure widget, ignoring any expections thrown. This ensures that
    # problems deconfiguing one widget doesn't interfere with deconfiguring
    # any other widget, and doesn't interfere with its (or any other widget's)
    # altimate destruction.
    try:
        _Deconfigure(
            self,
            lambda config: config in self.keys(),
            self.cget,
            self.__atkObj)
    except:
        pass

###
### class Toplevel hooks.
###

# Add an interfaces query method to class Toplevel.
def _Toplevel_atk_ifaces(self):
    return Wm._atk_ifaces(self) | BaseWidget._atk_ifaces(self)
Toplevel._atk_ifaces = _Toplevel_atk_ifaces

# Hook for class Toplevel's __init__ method.
def _Toplevel__init__(self, *args, **kwargs):

    self._atk_object()

    Toplevel.__original__init__Tka11y(self, *args, **kwargs)

    self.__atkObj.name = self.wm_title().encode('utf-8')
    self.__atkObj.SetState(atk.ATK_STATE_RESIZABLE)

    self.__atkObj.component_get_layer = lambda: _SPI_LAYER_WINDOW

    def maximize():
        try:
            self.state('zoomed')
        except:
            # Tk doesn't provide a way to maximize the window, so this is the
            # best we can do. Unfortunately, the 'restore' action will not
            # restore to the previous size in this case.
            self.wm_geometry('%dx%d+0+0' % self.maxsize())

    self.__atkObj.AddAction('close', func=self.destroy)
    self.__atkObj.AddAction('maximize', func=maximize)
    self.__atkObj.AddAction('minimize', func=self.wm_iconify)
    self.__atkObj.AddAction('restore', func=self.wm_deiconify)

Toplevel.__original__init__Tka11y = Toplevel.__init__
Toplevel.__init__ = _Toplevel__init__

###
### class Button hooks.
###

# Add an interfaces query method to class Button.
def _Button_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_TEXT
Button._atk_ifaces = _Button_atk_ifaces

# Hook for class Button's __init__ method.
def _Button__init__(self, *args, **kwargs):

    self._atk_object()

    Button.__original__init__Tka11y(self, *args, **kwargs)

    # Key bindings for buttons are not automatically set up, so the value
    # returned here may not be correct. However, if the underline option has
    # been specified, the assumption is made that the binding has also been
    # made (i.e., via the bind method).
    def get_click_action_keybinding():
        keyPosition = self['underline']
        if keyPosition >= 0:
            return '<Alt>' + self['text'][keyPosition].upper()
        else:
            return None

    def do_click_action():
        self.after_idle(self.invoke)
        return True

    self.__atkObj.AddAction('click',
        keybinding=get_click_action_keybinding,
        func=do_click_action)

Button.__original__init__Tka11y = Button.__init__
Button.__init__ = _Button__init__

###
### class Canvas hooks.
###

# None required.

###
### class Checkbutton hooks.
###

# Add an interfaces query method to class Checkbutton.
def _Checkbutton_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_TEXT
Checkbutton._atk_ifaces = _Checkbutton_atk_ifaces

# Hook for class Checkbutton's __init__ method.
def _Checkbutton__init__(self, *args, **kwargs):

    self._atk_object()

    Checkbutton.__original__init__Tka11y(self, *args, **kwargs)

    # Key bindings for buttons are not automatically set up, so the value
    # returned here may not be correct. However, if the underline option has
    # been specified, the assumption is made that the binding has also been
    # made (i.e., via the bind method).
    def get_click_action_keybinding():
        keyPosition = self['underline']
        if keyPosition >= 0:
            return '<Alt>' + self['text'][keyPosition].upper()
        else:
            return None

    def do_click_action():
        self.after_idle(self.invoke)
        return True

    self.__atkObj.AddAction('click',
        keybinding=get_click_action_keybinding,
        func=do_click_action)

Checkbutton.__original__init__Tka11y = Checkbutton.__init__
Checkbutton.__init__ = _Checkbutton__init__

###
### class Entry hooks.
###

# Add an interfaces query method to class Entry.
def _Entry_atk_ifaces(self):
    return \
        Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_TEXT | \
        atk.ATK_IFACE_EDITABLE_TEXT
Entry._atk_ifaces = _Entry_atk_ifaces

# Hook for class Entry's __init__ method.
def _Entry__init__(self, *args, **kwargs):

    self._atk_object()

    Entry.__original__init__Tka11y(self, *args, **kwargs)

    self.__atkObj.text_get_character_count = \
        lambda: len(self.get())

    def getSecureText():
        text = self.get()
        if self['show'] != '':
            text = len(text) * self['show'][0]
        return text

    def get_text(start, end):
        if end < 0: end = None
        return getSecureText()[start:end].encode('utf-8')
    self.__atkObj.text_get_text = get_text

    self.__atkObj.text_get_caret_offset = \
        lambda: self.index(INSERT)

    self.__atkObj.text_set_caret_offset = \
        lambda offset: self.icursor(offset)

    def set_text_contents(contents):
        self.delete(0, END)
        self.insert(0, contents.decode('utf-8'))
    self.__atkObj.editable_set_text_contents = set_text_contents

    def insert_text(s, length, position):
        if length < 0: length = None
        self.icursor(position)
        self.insert(position, s[:length])
    self.__atkObj.editable_insert_text = insert_text

    def delete_text(start, end):
        if end < 0: end = END
        self.icursor(start)
        self.delete(start, end)
    self.__atkObj.editable_delete_text = delete_text

Entry.__original__init__Tka11y = Entry.__init__
Entry.__init__ = _Entry__init__

###
### class Frame hooks.
###

# None required.

###
### class Label hooks.
###

# Add an interfaces query method to class Label.
def _Label_atk_ifaces(self):
    return Widget._atk_ifaces(self) | atk.ATK_IFACE_TEXT
Label._atk_ifaces = _Label_atk_ifaces

###
### class Listbox hooks.
###

# Add an interfaces query method to class Listbox.
def _Listbox_atk_ifaces(self):
    return Widget._atk_ifaces(self) | atk.ATK_IFACE_SELECTION
Listbox._atk_ifaces = _Listbox_atk_ifaces

# Hook for class Listbox's __init__ method.
def _Listbox__init__(self, *args, **kwargs):

    self._atk_object()

    Listbox.__original__init__Tka11y(self, *args, **kwargs)

    def add_selection(i):
        self.selection_set(i)
        self.__atkObj.ref_accessible_child(i).SetState(atk.ATK_STATE_SELECTED)
    self.__atkObj.selection_add_selection = add_selection

    def clear_selection():
        self.selection_clear(0, END)
        for i in range(self.__atkObj.n_accessible_children):
            self.__atkObj.ref_accessible_child(i).SetState \
                (atk.ATK_STATE_SELECTED, False)
    self.__atkObj.selection_clear_selection = clear_selection

    def ref_selection(i):
        return self.__atkObj.ref_accessible_child(i)
    self.__atkObj.selection_ref_selection = ref_selection

    def get_selection_count():
        return len(self.curselection())
    self.__atkObj.selection_get_selection_count = get_selection_count

    def is_child_selected(i):
        return self.selection_includes(i)
    self.__atkObj.selection_is_child_selected = is_child_selected

    def remove_selection(i):
        self.selection_clear(i)
        self.__atkObj.ref_accessible_child(i).SetState \
            (atk.ATK_STATE_SELECTED, False)
        return self.__atkObj.selection_is_child_selected()
    self.__atkObj.selection_remove_selection = remove_selection

    def select_all_selection():
        self.selection_set(0, END)
        for i in range(self.__atkObj.n_accessible_children):
            self.__atkObj.ref_accessible_child(i).SetState \
                (atk.ATK_STATE_SELECTED)
        return self.__atkObj.selection_get_selection_count() == self.size()
    self.__atkObj.selection_select_all_selection = select_all_selection

Listbox.__original__init__Tka11y = Listbox.__init__
Listbox.__init__ = _Listbox__init__

# Hook for class Listbox's insert method.
def _Listbox_insert(self, index, *items):

    oldSize = self.size()
    insertIndex = self.index(index)

    self.__atkObj._bypassVariableUpdate = True
    Listbox.__original_insert_Tka11y(self, index, *items)
    del self.__atkObj._bypassVariableUpdate

    # Temporarily detach item accessibility objects after the insertion point.
    # They will be reattached after the new ones have been inserted in order
    # to maintain proper order.
    atkItemObjs = []
    for i in range(insertIndex, oldSize):
        atkItemObj = self.__atkObj.ref_accessible_child(insertIndex)
        atkItemObjs.append(atkItemObj)
        atkItemObj.parent = None

    # Insert new list item accessibility objects.
    for item in items:
        _Listbox_appendItem(self, item)

    # Reattach list item accessibility objects following the inserted ones.
    for aio in atkItemObjs:
        aio.parent = self.__atkObj

Listbox.__original_insert_Tka11y = Listbox.insert
Listbox.insert = _Listbox_insert

def _Listbox_appendItem(listbox, item):

    index = listbox.__atkObj.n_accessible_children

    atkItemObj = _AtkObject(
        atk.ATK_IFACE_COMPONENT |
        atk.ATK_IFACE_ACTION |
        atk.ATK_IFACE_TEXT)
    atkItemObj.role = atk.ATK_ROLE_LIST_ITEM
    atkItemObj.SetState(atk.ATK_STATE_SELECTABLE)
    atkItemObj.name = unicode(item).encode('utf-8')
    atkItemObj.description = listbox.widgetName + ' item'
    atkItemObj.parent = listbox.__atkObj

    def get_extents(coord_type, atkItemObj):
        return \
            atkItemObj.component_get_position(coord_type) + \
            atkItemObj.component_get_size(coord_type)
    atkItemObj.component_get_extents = \
        lambda coord_type, aio=atkItemObj: get_extents(coord_type, aio)

    def get_position(coord_type, atkItemObj):
        itemIndex = atkItemObj.index_in_parent
        listboxPos = atkItemObj.parent.component_get_position(coord_type)
        itemBox = listbox.bbox(itemIndex)
        if itemBox == None:
            return 0, 0
        else:
            return tuple([listboxPos[i] + itemBox[i] for i in range(2)])
    atkItemObj.component_get_position = \
        lambda coord_type, aio=atkItemObj: get_position(coord_type, aio)

    def get_size(coord_type, atkItemObj):
        itemIndex = atkItemObj.index_in_parent
        itemBox = listbox.bbox(itemIndex)
        if itemBox == None:
            return 0, 0
        else:
            return itemBox[2:4]
    atkItemObj.component_get_size = \
        lambda coord_type, aio=atkItemObj: get_size(coord_type, aio)

    atkItemObj.component_get_layer = lambda: _SPI_LAYER_WIDGET

    def grab_focus(atkItemObj):
        itemIndex = atkItemObj.index_in_parent
        listbox.activate(itemIndex)
        return True
    atkItemObj.component_grab_focus = lambda aio=atkItemObj: grab_focus(aio)

    def isItemConfig(config):
        # Return true if configurable is available for either the item or
        # for the item's Listbox.
        itemIndex = atkItemObj.index_in_parent
        return \
            config in listbox.itemconfig(itemIndex) or \
            config in listbox.keys()

    def getItemConfig(config, textIndex):
        # Try getting configuration value from the item, falling back to the
        # item's Listbox if the configuration value is not set for the item.
        itemIndex = atkItemObj.index_in_parent
        value = None
        if config in listbox.itemconfig(itemIndex):
            value = listbox.itemcget(itemIndex, config)
        if not value and config in listbox.keys():
            value = listbox.cget(config)
        return value

    # Cache default text attribute values if not already done.
    for configName in _textAttributeConfigKeys.keys():
        defaultConfigKey = ((Listbox, 'item'), configName)
        if defaultConfigKey not in _defaultConfigCache:
            attribId, formatFunc = _textAttributeConfigKeys[configName]
            defaultValue = formatFunc(
                (listbox, 'item', index),
                isItemConfig, getItemConfig, configName, -1)
            _defaultConfigCache[defaultConfigKey] = defaultValue

    def get_text_character_count():
        itemIndex = atkItemObj.index_in_parent
        return len(unicode(listbox.get(itemIndex)))
    atkItemObj.text_get_character_count = get_text_character_count

    def get_text(start, end):
        itemIndex = atkItemObj.index_in_parent
        return unicode(listbox.get(itemIndex))[start:end].encode('utf-8')
    atkItemObj.text_get_text = get_text

    atkItemObj.text_get_character_at_offset = \
        lambda offset: atkItemObj.text_get_text(offset, offset + 1)

    def getTextAttribute(configName, textIndex=-1):
        itemIndex = atkItemObj.index_in_parent
        return _GetTextAttribute(
                (listbox, 'item', itemIndex),
                isItemConfig, getItemConfig, configName, textIndex)
    atkItemObj._tkGetTextAttribute = getTextAttribute

    atkItemObj.text_get_default_attributes = \
        lambda: _GetDefaultTextAttributes(atkItemObj)

    atkItemObj.text_get_run_attributes = \
        lambda offset: _GetTextRunAttributes(atkItemObj, offset)

    # Define a test to check whether the listbox responds to click events.
    # Used below.
    def respondsTo(sequences):
        # Check if any of the given sequences are present in the widget's own
        # bindings.
        if len(set(listbox.bind()).intersection(sequences)) > 0:
            return True

        # Check if any of the given sequences are present in any of the bindings
        # identified by the widget's bind tags.
        for tag in listbox.bindtags():
            if tag in _taggedSequences:
                if len(set(_taggedSequences[tag]).intersection(sequences)) > 0:
                    return True

        # No matches.
        return False

    # For a listbox that responds to click events, add appropriate actions
    # to its items.
    if respondsTo(_clickSequences):
        atkItemObj.AddAction('click',
             func=lambda: _ClickListBoxItem(listbox, atkItemObj, 1))
    if respondsTo(_doubleClickSequences):
        atkItemObj.AddAction('double-click',
             func=lambda: _ClickListBoxItem(listbox, atkItemObj, 2))

    _Configure(
        (listbox, index),
        lambda config: config in listbox.itemconfig(index),
        lambda config: listbox.itemcget(index, config),
        atkItemObj)

# Hook for class Listbox's delete method.
def _Listbox_delete(self, first, last = None):

    begin = self.index(first)
    if last == None:
        end = begin + 1
    else:
        end = self.index(last)
    if end > self.size():
        end = self.size()

    for i in range(begin, end):
        atkItemObj = self.__atkObj.ref_accessible_child(begin)
        _Deconfigure(
            (self, begin),
            lambda config: config in self.itemconfig(begin),
            lambda config: self.itemcget(begin, config),
            atkItemObj)
        atkItemObj.parent = None

    self.__atkObj._bypassVariableUpdate = True
    Listbox.__original_delete_Tka11y(self, first, last)
    del self.__atkObj._bypassVariableUpdate

Listbox.__original_delete_Tka11y = Listbox.delete
Listbox.delete = _Listbox_delete

# Hook for class Listbox's itemconfigure method.
def _Listbox_itemconfigure(self, index, cnf = None, **kwargs):

    configs = {}
    if kwargs:
        configs = Tkinter._cnfmerge((cnf, kwargs))
    elif cnf:
        configs = Tkinter._cnfmerge(cnf)

    if len(configs) > 0:
        atkItemObj = self.__atkObj.ref_accessible_child(index)
        _Deconfigure(
            (self, index),
            lambda config: config in configs,
            lambda config: self.itemcget(index, config),
            atkItemObj)

    result = Listbox.__original_itemconfigure_Tka11y \
        (self, index, cnf=cnf, **kwargs)

    if len(configs) > 0:
        _Configure(
            (self, index),
            lambda config: config in configs,
            lambda config: self.itemcget(index, config),
            atkItemObj)

    return result

Listbox.__original_itemconfigure_Tka11y = Listbox.itemconfigure
Listbox.itemconfigure = _Listbox_itemconfigure
Listbox.itemconfig = Listbox.itemconfigure

###
### class Menu hooks.
### Note that additional menu support is implemented in a hook to class Misc's
### configure method (menu key).
###

# Hook for class Menu's __init__ method.
def _Menu__init__(self, master=None, cnf={}, **kwargs):

    self._atk_object()

    Menu.__original__init__Tka11y(self, master, cnf, **kwargs)

    self.__atkObj.role = atk.ATK_ROLE_MENU

    # Defer parent identification until the menu's relationship with other
    # widgets (i.e., toplevels or other menus) is given.
    self.__atkObj.parent = None

    if self['tearoff']:
        _MenuInsert(self, 0, 'tearoff')

Menu.__original__init__Tka11y = Menu.__init__
Menu.__init__ = _Menu__init__

# Hook for class Menu's internal add method.
def _Menu_add(self, entryType, cnf={}, **kwargs):

    # Determine index of insertion point for append operation. Note that for
    # END, the index method returns the index of the last item. It returns
    # None if there are no items.
    appendIndex = self.index(END)
    if appendIndex == None:
        appendIndex = 0
    else:
        appendIndex += 1

    _MenuInsert(self, appendIndex, entryType,
        lambda cnf, kwargs: Menu.__original_add_Tka11y
            (self, entryType, cnf=cnf, **kwargs),
        cnf=cnf, **kwargs)

Menu.__original_add_Tka11y = Menu.add
Menu.add = _Menu_add

# Hook for class Menu's internal insert method.
def _Menu_insert(self, index, entryType, cnf={}, **kwargs):

    # Determine real insertion point. Note that for END, the index method
    # returns the index of the last item. It returns None if there are no items.
    insertIndex = self.index(index)
    if insertIndex == None:
        insertIndex = 0
    if index == END:
        insertIndex += 1

    _MenuInsert(self, insertIndex, entryType,
        lambda cnf, kwargs: Menu.__original_insert_Tka11y
            (self, index, entryType, cnf=cnf, **kwargs),
        cnf=cnf, **kwargs)

Menu.__original_insert_Tka11y = Menu.insert
Menu.insert = _Menu_insert

# Common Menu add/insert logic.
def _MenuInsert(menu, index, entryType, originalFunc=None, cnf={}, **kwargs):

    #configs = Tkinter._cnfmerge((cnf, kwargs))
    configs = {}
    if kwargs:
        configs = Tkinter._cnfmerge((cnf, kwargs))
    elif cnf:
        configs = Tkinter._cnfmerge(cnf)

    # Mimic Tk's behavior of keeping the tearoff menu item the first item
    # in the list.
    if entryType != 'tearoff' and menu['tearoff'] and index == 0:
        index = 1

    # Prepare to cache default text attribute values for each unique menu
    # entry type/attribute pair. This is done upon the addition of the first of
    # each unique type of menu entry. If this entry is being created with
    # non-default text attributes, application of those attributes is deferred
    # until we can obtain those attributes' default values, after which the
    # attributes are applied, below.
    deferredConfigs = {}
    cacheKeys = []
    for configName in _textAttributeConfigKeys.keys():
        defaultConfigKey = ((Menu, entryType), configName)
        if defaultConfigKey not in _defaultConfigCache:
            cacheKeys.append(defaultConfigKey)
            for configNameAlias in _AttributeConfigNameAliases(configName):
                if configNameAlias in configs:
                    deferredConfigs[configNameAlias] = configs[configNameAlias]
                    if configNameAlias in cnf:
                        del cnf[configNameAlias]
                    if configNameAlias in kwargs:
                        del kwargs[configNameAlias]

    # Call the original add/insert routine, possibly without some keyword
    # parameters. These will be applied below, after their default values have
    # been cached.
    if callable(originalFunc):
        originalFunc(cnf, kwargs)

    # Temporarily detach item accessibility objects after the insertion point.
    # They will be reattached after the new one has been inserted in order
    # to maintain proper order.
    oldSize = menu.index(END)
    atkEntryObjs = []
    for i in range(index, oldSize):
        atkEntryObj = menu.__atkObj.ref_accessible_child(index)
        atkEntryObjs.append(atkEntryObj)
        atkEntryObj.parent = None

    ifaces = 0
    if entryType != 'separator':
        ifaces |= atk.ATK_IFACE_ACTION
    ifaces |= atk.ATK_IFACE_TEXT

    atkEntryObj = _AtkObject(ifaces)
    atkEntryObj.parent = menu.__atkObj
    atkEntryObj._tkMenu = menu

    def isEntryConfig(config):
        # Return true if configurable is available for either the entry or,
        # if it makes sense, for the entry's Menu.
        entryIndex = atkEntryObj.index_in_parent
        entryOnlyConfigs = ['selectcolor']
        return \
            config in menu.entryconfig(entryIndex) or \
            config not in entryOnlyConfigs and config in menu.keys()

    def getEntryConfig(config, textIndex):
        # Try getting configuration value from the entry, falling back to
        # the entry's Menu if the configuration value is not set for the
        # entry.
        entryIndex = atkEntryObj.index_in_parent
        value = None
        if config in menu.entryconfig(entryIndex):
            value = menu.entrycget(entryIndex, config)
        if not value and config in menu.keys():
            value = menu.cget(config)
        return value

    # Cache any default text attribute values identified earlier.
    for defaultConfigKey in cacheKeys:
        klass, configName = defaultConfigKey
        attribId, formatFunc = _textAttributeConfigKeys[configName]
        defaultValue = formatFunc(
            (menu, entryType, index),
            isEntryConfig, getEntryConfig, configName, -1)
        _defaultConfigCache[defaultConfigKey] = defaultValue

    # Apply any deferred configuration items now that default text attribute
    # values have been cached.
    for configName, value in deferredConfigs.iteritems():
        eval('menu.entryconfig(index, %s=value)' % configName)

    if 'label' in menu.entryconfig(index):
        atkEntryObj.name_config = 'label'

    if entryType == 'cascade':
        atkEntryObj.role = atk.ATK_ROLE_MENU
        atkEntryObj.description = 'sub%s' % menu.widgetName
        atkEntryObj.SetState(atk.ATK_STATE_EXPANDABLE)
    elif entryType == 'tearoff':
        atkEntryObj.role = atk.ATK_ROLE_TEAR_OFF_MENU_ITEM
        atkEntryObj.description = 'tear off %s item' % menu.widgetName
    elif entryType == 'separator':
        atkEntryObj.role = atk.ATK_ROLE_SEPARATOR
        atkEntryObj.description = '%s item separator' % menu.widgetName
    elif entryType == 'checkbutton':
        atkEntryObj.role = atk.ATK_ROLE_CHECK_MENU_ITEM
        atkEntryObj.description = 'check button %s item' % menu.widgetName
    elif entryType == 'radiobutton':
        atkEntryObj.role = atk.ATK_ROLE_RADIO_MENU_ITEM
        atkEntryObj.description = 'radio button %s item' % menu.widgetName
    else: # 'command'
        atkEntryObj.role = atk.ATK_ROLE_MENU_ITEM
        atkEntryObj.description = '%s item' % menu.widgetName

    if ifaces & atk.ATK_IFACE_ACTION:

        def get_click_action_local_keybinding(atkObj):
            entryIndex = atkObj.index_in_parent
            keyPosition = atkObj._tkMenu.entrycget(entryIndex, 'underline')
            if keyPosition >= 0:
                label = atkObj._tkMenu.entrycget(entryIndex, 'label')
                return label[keyPosition].upper()
            else:
                raise Exception, 'No underline'
        def get_click_action_full_keybinding(atkObj):
            if atkObj == None or atkObj.role not in _atkMenuContentRoles:
                return ''
            else:
                parentBinding = \
                    get_click_action_full_keybinding(atkObj.parent)
                if parentBinding != '':
                    parentBinding = parentBinding + ':'
                return \
                    parentBinding + \
                    get_click_action_local_keybinding(atkObj)
        def get_click_action_keybinding():
            bindingSpec = ''
            try:
                localBinding = get_click_action_local_keybinding(atkEntryObj)
                if localBinding != '':
                    bindingSpec = '<Alt>' + localBinding
            except:
                pass
            try:
                fullBinding = get_click_action_full_keybinding(atkEntryObj)
                if fullBinding:
                    bindingSpec = bindingSpec + ';<Alt>' + fullBinding
            except:
                pass
            if bindingSpec != '':
                return bindingSpec
            else:
                return None

        def do_action(func):
            entryIndex = atkEntryObj.index_in_parent
            menu.after_idle(lambda: func(entryIndex))
            return True

        def do_click_action():
            entryIndex = atkEntryObj.index_in_parent
            menu.after_idle(lambda: menu.activate(entryIndex))
            menu.after_idle(lambda: menu.invoke(entryIndex))
            return True

        atkEntryObj.AddAction('activate',
             description='Activate as if mouse-over occurred',
             func=lambda: do_action(menu.activate))
        atkEntryObj.AddAction('invoke',
             description='Invoke associated command',
             func=lambda: do_action(menu.invoke))
        atkEntryObj.AddAction('click',
             description='Perform both activate and invoke',
             keybinding=get_click_action_keybinding,
             func=do_click_action)

    if ifaces & atk.ATK_IFACE_TEXT:

        def get_text_character_count():
            entryIndex = atkEntryObj.index_in_parent
            if 'label' not in menu.entryconfig(entryIndex):
                return 0
            return len(menu.entrycget(entryIndex, 'label'))
        atkEntryObj.text_get_character_count = get_text_character_count

        def get_text(start, end):
            entryIndex = atkEntryObj.index_in_parent
            return menu.entrycget(entryIndex, 'label') \
                [start:end].encode('utf-8')
        atkEntryObj.text_get_text = get_text

        atkEntryObj.text_get_character_at_offset = \
            lambda offset: atkEntryObj.text_get_text(offset, offset + 1)

        def getTextAttribute(configName, textIndex=-1):
            entryIndex = atkEntryObj.index_in_parent
            return _GetTextAttribute(
                (menu, entryType, entryIndex),
                isEntryConfig, getEntryConfig, configName, textIndex)
        atkEntryObj._tkGetTextAttribute = getTextAttribute

        atkEntryObj.text_get_default_attributes = \
            lambda: _GetDefaultTextAttributes(atkEntryObj)

        atkEntryObj.text_get_run_attributes = \
            lambda offset: _GetTextRunAttributes(atkEntryObj, offset)

    if entryType == 'checkbutton' or entryType == 'radiobutton':
        Variable._atk_vars.add(
            menu.entrycget(index, 'variable'),
            (menu, atkEntryObj), 'variable')

    _Configure(
        (menu, index),
        lambda config: config in menu.entryconfig(index),
        lambda config: menu.entrycget(index, config),
        atkEntryObj)

    # Reattach item accessibility objects following the inserted one.
    for aio in atkEntryObjs:
        aio.parent = menu.__atkObj

# Hook for class Menu's delete method.
def _Menu_delete(self, index1, index2 = None):

    begin = self.index(index1)
    if index2 == None:
        end = begin + 1
    else:
        end = self.index(index2)
        if end == None:
            end = 0
        else:
            end += 1

    # Mimic Tk's behavior of not deleting the tearoff menu item.
    if self['tearoff'] and begin == 0:
        begin += 1

    if begin != None:
        for i in range(begin, end):
            atkEntryObj = self.__atkObj.ref_accessible_child(begin)

            _Deconfigure(
                (self, begin),
                lambda config: config in self.entryconfig(begin),
                lambda config: self.entrycget(begin, config),
                atkEntryObj)

            atkEntryObj.parent = None

    Menu.__original_delete_Tka11y(self, index1, index2)

Menu.__original_delete_Tka11y = Menu.delete
Menu.delete = _Menu_delete

# Hook for class Menu's entryconfigure method.
def _Menu_entryconfigure(self, index, cnf=None, **kwargs):

    #configs = Tkinter._cnfmerge((cnf, kwargs))
    configs = {}
    if kwargs:
        configs = Tkinter._cnfmerge((cnf, kwargs))
    elif cnf:
        configs = Tkinter._cnfmerge(cnf)

    if len(configs) > 0:
        atkEntryObj = self.__atkObj.ref_accessible_child(index)
        _Deconfigure(
            (self, index),
            lambda config: config in configs,
            lambda config: self.entrycget(index, config),
            atkEntryObj)

    result = Menu.__original_entryconfigure_Tka11y \
        (self, index, cnf=cnf, **kwargs)

    if len(configs) > 0:
        _Configure(
            (self, index),
            lambda config: config in configs,
            lambda config: self.entrycget(index, config),
            atkEntryObj)

    return result

Menu.__original_entryconfigure_Tka11y = Menu.entryconfigure
Menu.entryconfigure = _Menu_entryconfigure
Menu.entryconfig = Menu.entryconfigure

# Hook for class Menu's post method.
def _Menu_post(self, *args, **kwargs):

    Menu.__original_post_Tka11y(self, *args, **kwargs)

    if self.__atkObj.parent == None:
        #self.__atkObj.parent = _atkApp
        self.__atkObj.parent = self.master.__atkObj

Menu.__original_post_Tka11y = Menu.post
Menu.post = _Menu_post

# Hook for class Menu's unpost method.
def _Menu_unpost(self, *args, **kwargs):

    Menu.__original_unpost_Tka11y(self, *args, **kwargs)

    self.__atkObj.parent = None

Menu.__original_unpost_Tka11y = Menu.unpost
Menu.unpost = _Menu_unpost

###
### class Menubutton hooks.
###

# Add an interfaces query method to class Menubutton.
def _Menubutton_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_TEXT
Menubutton._atk_ifaces = _Menubutton_atk_ifaces

###
### class Message hooks.
###

# Add an interfaces query method to class Message.
def _Message_atk_ifaces(self):
    return Widget._atk_ifaces(self) | atk.ATK_IFACE_TEXT
try:
    Message._atk_ifaces = _Message_atk_ifaces
except:
    pass

###
### class Radiobutton hooks.
###

# Add an interfaces query method to class Radiobutton.
def _Radiobutton_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_TEXT
Radiobutton._atk_ifaces = _Radiobutton_atk_ifaces

# Hook for class Radiobutton's __init__ method.
def _Radiobutton__init__(self, *args, **kwargs):

    self._atk_object()

    Radiobutton.__original__init__Tka11y(self, *args, **kwargs)

    # Key bindings for buttons are not automatically set up, so the value
    # returned here may not be correct. However, if the underline option has
    # been specified, the assumption is made that the binding has also been
    # made (i.e., via the bind method).
    def get_click_action_keybinding():
        keyPosition = self['underline']
        if keyPosition >= 0:
            return '<Alt>' + self['text'][keyPosition].upper()
        else:
            return None

    def do_click_action():
        self.after_idle(self.invoke)
        return True

    self.__atkObj.AddAction('click',
        keybinding=get_click_action_keybinding,
        func=do_click_action)

Radiobutton.__original__init__Tka11y = Radiobutton.__init__
Radiobutton.__init__ = _Radiobutton__init__

###
### class Scale hooks.
###

# Add an interfaces query method to class Scale.
def _Scale_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_TEXT | \
        atk.ATK_IFACE_VALUE
Scale._atk_ifaces = _Scale_atk_ifaces

# Hook for class Scale's __init__ method.
def _Scale__init__(self, *args, **kwargs):

    self._atk_object()

    Scale.__original__init__Tka11y(self, *args, **kwargs)

    def get_current_value():
        return self.get()
    self.__atkObj.value_get_current_value = get_current_value

    def set_current_value(value):
        min = self.get_minimum_value()
        max = self.get_maximum_value()
        if value < min:
            value = min
        elif value > max:
            value = max
        self.set(value)
        return self.get() == value
    self.__atkObj.value_set_current_value = set_current_value

    def get_minimum_value():
        return self.cget('from')
    self.__atkObj.value_get_minimum_value = get_minimum_value

    def get_maximum_value():
        return self.cget('to')
    self.__atkObj.value_get_maximum_value = get_maximum_value

    def get_minimum_increment():
        return self.cget('resolution')
    self.__atkObj.value_get_minimum_increment = get_minimum_increment

Scale.__original__init__Tka11y = Scale.__init__
Scale.__init__ = _Scale__init__

###
### class Scrollbar hooks.
###

# Add an interfaces query method to class Scrollbar.
def _Scrollbar_atk_ifaces(self):
    return \
        Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_VALUE
Scrollbar._atk_ifaces = _Scrollbar_atk_ifaces

# Hook for class Scrollbar's __init__ method.
def _Scrollbar__init__(self, *args, **kwargs):

    self._atk_object()

    Scrollbar.__original__init__Tka11y(self, *args, **kwargs)

    def do_scroll_action(number, what):
        viewCommand = self['command']
        if viewCommand:
            self.after_idle \
                (lambda: self.tk.call(viewCommand, 'scroll', number, what))
            return True
        else:
            return False

    self.__atkObj.AddAction('scroll-unit-less',
        description='Scroll up/left 1 unit',
        func=lambda: do_scroll_action('-1', 'units'))
    self.__atkObj.AddAction('scroll-unit-more',
        description='Scroll down/right 1 unit',
        func=lambda: do_scroll_action('1', 'units'))
    self.__atkObj.AddAction('scroll-page-less',
        description='Scroll up/left 1 page',
        func=lambda: do_scroll_action('-1', 'pages'))
    self.__atkObj.AddAction('scroll-page-more',
        description='Scroll down/right 1 page',
        func=lambda: do_scroll_action('1', 'pages'))

    def get_current_value():
        low, high = self.get()
        return float(low) / (1 - high + low)
    self.__atkObj.value_get_current_value = get_current_value

    def set_current_value(value):
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        low, high = self.get()
        newLow = value * (1 - high + low)
        viewCommand = self['command']
        if viewCommand:
            self.tk.call(viewCommand, 'moveto', str(newLow))
        else:
            newHigh = newLow + high - low
            overshoot = newHigh - 1
            if overshoot > 1:
                newHigh = 1
                newLow -= overshoot
            self.set(newLow, newHigh)
        return True
    self.__atkObj.value_set_current_value = set_current_value

    self.__atkObj.value_get_minimum_value = lambda: 0

    self.__atkObj.value_get_maximum_value = lambda: 1

    self.__atkObj.value_get_minimum_increment = lambda: 0

Scrollbar.__original__init__Tka11y = Scrollbar.__init__
Scrollbar.__init__ = _Scrollbar__init__

###
### class Text hooks.
###

# Add an interfaces query method to class Text.
def _Text_atk_ifaces(self):
    return \
        Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_TEXT | \
        atk.ATK_IFACE_EDITABLE_TEXT
Text._atk_ifaces = _Text_atk_ifaces

# Hook for class Text's __init__ method.
def _Text__init__(self, *args, **kwargs):

    self._atk_object()

    Text.__original__init__Tka11y(self, *args, **kwargs)

    def get_character_count():
        count = 0
        for key, value, index in self.dump('1.0', 'end-1c'):
            if key == 'text':
                count += len(value)
            elif key != 'mark' and key[0:3] != 'tag':
                count += 1
        return count
    self.__atkObj.text_get_character_count = get_character_count

    def get_text(start, end):
        if end < 0:
            endIndex = 'end-1c'
        else:
            endIndex = '1.0+%dc' % end
        texts = []
        for key, value, index in self.dump('1.0+%dc' % start, endIndex):
            if key == 'text':
                texts.append(unicode(value))
            elif key != 'mark' and key[0:3] != 'tag':
                # Non-text items (e.g., images, windows) take up a position.
                if key == 'image':
                    texts.append(u'\u24D8') # circled latin small letter i
                elif key == 'window':
                    #texts.append(u'\u24B2') # circled latin small letter w
                    texts.append(u'\u24CC') # circled latin capital letter w
                else:
                    texts.append(u'\u229B') # circled asterisk operator
        return u''.join(texts).encode('utf-8')
    self.__atkObj.text_get_text = get_text

    def isCharacterConfig(configName):
        return configName == 'underline' or configName in self.keys()

    def getCharacterConfig(configName, index):
        try:
            value = self.cget(configName)
        except:
            value = ''
        assert index >= 0
        textIndex = '1.0+%dc' % index
        for tagName in self.tag_names(textIndex):
            if configName in self.tag_config(tagName):
                tagValue = self.tag_cget(tagName, configName)
                if tagValue:
                    value = tagValue
        return value

    def getTextAttribute(configName, index=-1):
        return _GetTextAttribute(
            self, isCharacterConfig, getCharacterConfig,
            configName, index)
    self.__atkObj._tkGetTextAttribute = getTextAttribute

    # Used for text_get_caret_offset and text_get_offset_at_point
    def get_mark_offset(mark):
        offset = 0
        for key, value, index in self.dump('1.0', END):
            if key == 'mark':
                if value == 'insert':
                    break
            elif key == 'text':
                offset += len(value)
            elif key[0:3] != 'tag':
                # Non-text items (e.g., images, windows) take up a position.
                offset += 1
        return offset
    self.__atkObj.text_get_caret_offset = \
        lambda: get_mark_offset(INSERT)

    def set_caret_offset(offset):
        self.mark_set(INSERT, '1.0+%dc' % offset)
    self.__atkObj.text_set_caret_offset = set_caret_offset

    self.__atkObj.text_get_offset_at_point = \
        lambda: get_mark_offset(CURRENT)

    def set_text_contents(contents):
        self.delete('1.0', END)
        self.insert(END, contents.decode('utf-8'))
    self.__atkObj.editable_set_text_contents = set_text_contents

    def insert_text(s, length, position):
        if length < 0: length = None
        set_caret_offset(position)
        self.insert('1.0+%dc' % position, s[:length])
    self.__atkObj.editable_insert_text = insert_text

    def delete_text(start, end):
        if end < 0:
            endIndex = END
        else:
            endIndex = '1.0+%dc' % end
        self.delete('1.0+%dc' % start, endIndex)
    self.__atkObj.editable_delete_text = delete_text

Text.__original__init__Tka11y = Text.__init__
Text.__init__ = _Text__init__

###
### class OptionMenu hooks.
###

# None required; this is a subclass of Menubutton.

###
### class Image hooks.
###

# Not implemented.

###
### class Spinbox hooks.
###

# Add an interfaces query method to class Spinbox.
def _Spinbox_atk_ifaces(self):
    return Widget._atk_ifaces(self) | \
        atk.ATK_IFACE_ACTION | \
        atk.ATK_IFACE_TEXT | \
        atk.ATK_IFACE_EDITABLE_TEXT
Spinbox._atk_ifaces = _Spinbox_atk_ifaces

# Hook for class Spinbox's __init__ method.
def _Spinbox__init__(self, *args, **kwargs):

    self._atk_object()

    Spinbox.__original__init__Tka11y(self, *args, **kwargs)

    def do_adjust_action(element):
        self.after_idle(lambda: self.invoke(element))
        return True

    self.__atkObj.AddAction('adjust-down',
        description='Decrease value by increment',
        func=lambda: do_adjust_action('buttondown'))
    self.__atkObj.AddAction('adjust-up',
        description='Increase value by increment',
        func=lambda: do_adjust_action('buttonup'))

    self.__atkObj.text_get_character_count = \
        lambda: len(self.get())

    def get_text(start, end):
        if end < 0: end = None
        return self.get()[start:end].encode('utf-8')
    self.__atkObj.text_get_text = get_text

    def set_text_contents(contents):
        self.delete(0, END)
        self.insert(0, contents.decode('utf-8'))
    self.__atkObj.editable_set_text_contents = set_text_contents

    def insert_text(s, length, position):
        if length < 0: length = None
        self.icursor(position)
        self.insert(position, s[:length])
    self.__atkObj.editable_insert_text = insert_text

    def delete_text(start, end):
        if end < 0: end = END
        self.delete(start, end)
    self.__atkObj.editable_delete_text = delete_text

try:
    Spinbox.__original__init__Tka11y = Spinbox.__init__
    Spinbox.__init__ = _Spinbox__init__
except:
    pass

###
### class LabelFrame hooks.
###

# Add an interfaces query method to class LabelFrame.
def _LabelFrame_atk_ifaces(self):
    return Widget._atk_ifaces(self) | atk.ATK_IFACE_TEXT
LabelFrame._atk_ifaces = _LabelFrame_atk_ifaces

###
### class PanedWindow hooks.
###

# None required.

###
### Miscellaneous.
###

class _AtkObject(atk.AtkObject):

    def __init__(self, ifaces):

        atk.AtkObject.__init__(self, ifaces)

        # Set up state management.
        self._stateSet = atk.AtkStateSet()
        def ref_state_set():
            return self._stateSet
        self.ref_state_set = ref_state_set

        # Redefine action interface methods.
        self.action_get_n_actions = self._getActionCount
        self.action_get_name = self._getActionName
        self.action_get_description = self._getActionDescription
        self.action_get_localized_name = self._getActionKeybinding
        self.action_get_keybinding = self._getActionKeybinding
        self.action_do_action = self._DoAction

    def SetState(self, state, on = True, notify = True):

        if on:
            success = self._stateSet.add_state(state)
        else:
            success = self._stateSet.remove_state(state)

        if success and notify:
            self.notify_state_change(state, on)
            #self.emit('AtkObject:visible-data-changed')

        return success

    def AddAction(self, name, description='', keybinding='', func=None,
        replace=True):

        if '_action_names' not in self.__dict__:
            self._action_names = []
            self._action_descriptions = []
            self._action_keybindings = []
            self._action_functions = []

        if name not in self._action_names:
            self._action_names.append(name)
            self._action_descriptions.append(description)
            self._action_keybindings.append(keybinding)
            self._action_functions.append(func)
        elif replace:
            index = self._action_names.index(name)
            self._action_descriptions[index] = description
            self._action_keybindings[index] = keybinding
            self._action_functions[index] = func

    # Internal methods...

    def _getActionCount(self):
        if '_action_names' not in self.__dict__:
            return 0
        else:
            return len(self._action_names)

    def _getActionName(self, i):
        try:
            return self._action_names[i]
        except:
            return None

    def _getActionDescription(self, i):
        try:
            return self._action_descriptions[i]
        except:
            return None

    def _getActionKeybinding(self, i):
        try:
            if callable(self._action_keybindings[i]):
                return self._action_keybindings[i]()
            else:
                return self._action_keybindings[i]
        except:
            return None

    def _DoAction(self, i):
        try:
            return self._action_functions[i]()
        except:
            return False

# Generic implementation for text_get_default_attributes method of the Text
# interface.
def _GetDefaultTextAttributes(atkObj):
    attribs = []
    for configName in _textAttributeConfigKeys.keys():
        attrib = atkObj._tkGetTextAttribute(configName)
        if attrib:
            attribs.append(attrib)
    return attribs

# Generic implementation for text_get_run_attributes method of the Text
# interface.
def _GetTextRunAttributes(atkObj, offset):
    charCount = atkObj.text_get_character_count()
    startOffset = offset
    endOffset = offset
    result = _GetExplicitTextAttributes(atkObj, offset)
    for offset in range(startOffset - 1, -1, -1):
        if not _AttributeListsEqual \
            (_GetExplicitTextAttributes(atkObj, offset), result):
            break
        startOffset -= 1
    for offset in range(endOffset + 1, charCount):
        if not _AttributeListsEqual \
            (_GetExplicitTextAttributes(atkObj, offset), result):
            break
        endOffset += 1
    if endOffset < charCount:
        endOffset += 1
    result.insert(0, startOffset)
    result.insert(1, endOffset)
    return result

# Text interface helper method to get explicit text attributes.
def _GetExplicitTextAttributes(atkObj, offset):
    attribs = []
    for configName in _textAttributeConfigKeys.keys():
        attrib = atkObj._tkGetTextAttribute(configName, offset)
        if attrib:
            defaultAttrib = \
                atkObj._tkGetTextAttribute(configName)
            if not _AttributesEqual(attrib, defaultAttrib):
                attribs.append(attrib)
    return attribs

# Text attribute query.
def _GetTextAttribute(widget, isConfig, getConfig, configName, index=-1):

    if configName not in _textAttributeConfigKeys or not isConfig(configName):
        return None

    if isinstance(widget, tuple):
        actualWidget, qualifier = widget[:2]
        widgetClass = (actualWidget.__class__, qualifier)
    else:
        actualWidget = widget
        widgetClass = widget.__class__

    attribId, formatFunc = _textAttributeConfigKeys[configName]
    attrib = atk.AtkAttribute()
    attrib.name = atk.text_attribute_get_name(attribId)
    if index == -1:
        value = _defaultConfigCache[(widgetClass, configName)]
    else:
        value = formatFunc(widget, isConfig, getConfig, configName, index)
    attrib.value = value
    return attrib

# Format a color attribute.
def _FormatColorAttribute(widget, isConfig, getConfig, configName, index):

    if not isConfig(configName):
        return None

    if isinstance(widget, tuple):
        actualWidget, qualifier = widget[:2]
        widgetClass = (actualWidget.__class__, qualifier)
    else:
        actualWidget = widget
        widgetClass = widget.__class__

    # Assign the appropriate color.
    color = getConfig(configName, index)
    if configName == 'selectcolor' and isConfig('variable'):
        # Determine the appropriate color for the check area in the
        # check button, radio button, or menu item variation of the same.
        variable = getConfig('variable', index)
        if isConfig('value'):
            value = getConfig('value', index)
        elif isConfig('onvalue'):
            value = getConfig('onvalue', index)
        else:
            assert False, 'Missing value or onvalue configuration'
        if unicode(actualWidget.getvar(variable)) == unicode(value):
            if isConfig('state') and getConfig('state', index) == DISABLED:
                color = getConfig('disabledforeground', index)
        else:
            color = getConfig('background', index)
    else:
        if isConfig('state') and getConfig('state', index) == DISABLED:
            disabledConfigName = _disabledColorConfigNames[configName]
            if isConfig(disabledConfigName):
                color = getConfig(disabledConfigName, index)
        elif widgetClass == (Listbox, 'item'):
            itemIndex = widget[2]
            if actualWidget.selection_includes(itemIndex):
                selectedConfigName = _selectedColorConfigNames[configName]
                if isConfig(selectedConfigName):
                    color = getConfig(selectedConfigName, index)

    # Convert '#rrggbb' to 'R,G,B', where r, g, and b are hexadecimal digits,
    # and R, G, and B are decimal values in the range [0-65535] (i.e., 16-bit
    # unsigned).
    return '%d,%d,%d' % actualWidget.winfo_rgb(color)

# Color attribute keys for widgets in the disabled state.
_disabledColorConfigNames = {
    'background': 'disabledbackground',
    'foreground': 'disabledforeground',
    }

# Color attribute keys for selected widget items.
_selectedColorConfigNames = {
    'background': 'selectbackground',
    'foreground': 'selectforeground',
    }

# Format an underline attribute.
def _FormatUnderlineAttribute(widget, isConfig, getConfig, configName, index):

    if widget.__class__ == Text:
        # Characters within Text widgets have a boolean value for the
        # underline configuration.
        underlineTrue = index != -1 and bool(getConfig(configName, index))
    else:
        # Most widgets have a position value for the underline configuration
        # which identifies which character is underlined.
        if not isConfig(configName):
            return None
        if index == -1:
            underlineTrue = False
        else:
            try:
                underlineTrue = int(getConfig(configName, index)) == index
            except:
                underlineTrue = False

    # Convert boolean to string representation.
    if underlineTrue:
        return 'single'
    else:
        return 'none'

# Text attribute configuration key data.
_textAttributeConfigKeys = {
    'underline': (_ATK_TEXT_ATTR_UNDERLINE, _FormatUnderlineAttribute),
    'background': (_ATK_TEXT_ATTR_BG_COLOR, _FormatColorAttribute),
    'foreground': (_ATK_TEXT_ATTR_FG_COLOR, _FormatColorAttribute),
    'selectcolor': (_ATK_TEXT_ATTR_INDICATOR_COLOR, _FormatColorAttribute),
    }

# Return a list of configuration names that all resolve to the given
# configuration name. For example, given 'background', the return value will
# be ['background', 'bg'].
def _AttributeConfigNameAliases(configName):
    result = [configName]
    if configName in _attributeConfigNameAliases:
        result += _attributeConfigNameAliases[configName]
    return result

# Attribute configuration name aliases.
_attributeConfigNameAliases = {
    'background': ['bg'],
    'foreground': ['fg'],
    }

# Attribute comparison.
def _AttributesEqual(attrib1, attrib2):
    if attrib1 == None or attrib2 == None:
        return attrib1 == None and attrib2 == None
    else:
        return \
            attrib1.name == attrib2.name and \
            attrib1.value == attrib2.value

# Attribute list comparison.
def _AttributeListsEqual(attribs1, attribs2):
    if len(attribs1) != len(attribs2):
        return False
    for i in range(len(attribs1)):
        if not _AttributesEqual(attribs1[i], attribs2[i]):
            return False
    return True

# After event to process ATK external interface.
_Atk_iterateDelay = 0
def _Atk_iterate(tk):
    global _Atk_iterateDelay
    try:
        # Run iteration. If there was any activity, schedule the next run
        # as soon as possible. Otherwise, delay a little longer than the last
        # time, up to the maximum delay.
        if _Atk_iterateDelay < Tka11yConstants.MaxAtkIterateDelay:
            _Atk_iterateDelay += Tka11yConstants.AtkIterateDelayStep
        while True:
            if not atk.iterate():
                break
            _Atk_iterateDelay = 0
        global _afterIterateId
        if _Atk_iterateDelay == 0:
            _afterIterateId = tk.after_idle(_Atk_iterate, tk)
        else:
            _afterIterateId = \
                tk.after(int(_Atk_iterateDelay), _Atk_iterate, tk)
    except:
        pass

if __name__ == '__main__':
    print 'To test Tka11y, run module Tka11y.test.'
    print 'To use Tka11y, import it and use it just like Tkinter.'
    print 'For example:'
    print '    import Tka11y as Tkinter'
    print 'or'
    print '    from Tka11y import *'
