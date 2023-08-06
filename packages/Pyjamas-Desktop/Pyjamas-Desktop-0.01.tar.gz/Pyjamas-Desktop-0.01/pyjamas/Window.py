"""
    Window provides access to the DOM model's global Window.
"""
import pygtk
pygtk.require('2.0')
import gtk

from pyjamas.__pyjamas__ import JS, doc, get_main_frame, wnd
import Location
closingListeners = []
resizeListeners = []

def addWindowCloseListener(listener):
    global closingListeners
    closingListeners.append(listener)

def addWindowResizeListener(listener):
    global resizeListeners
    resizeListeners.append(listener)

def alert(msg):
    JS("""
    window.alert("%s");
    """ % msg)

def confirm(msg):
    print "TODO", msg
    alert("Window.confirm() is still on the TODO list. sorry!")
    return False
    JS("""
    window.confirm("%s");
    """ % msg)

def enableScrolling(enable):
    doc().props.body.props.style.overflow = enable and 'auto' or 'hidden'
    JS("""
    $doc.body.style.overflow = enable ? 'auto' : 'hidden';
    """)

def getClientHeight():
    #height = wnd().props.inner_height
    #if height:
    #    return height
    return doc().props.body.props.client_height;
    JS("""
    if ($wnd.innerHeight)
        return $wnd.innerHeight;
    return $doc.body.clientHeight;
    """)

def getClientWidth():
    #width = wnd().props.inner_width
    #if width:
    #    return width
    return doc().props.body.props.client_width;
    JS("""
    if ($wnd.innerWidth)
        return $wnd.innerWidth;
    return $doc.body.clientWidth;
    """)

global location
location = None
def getLocation():
    global location
    if not location:
        print "FIXME: must get property 'location' from window, not string URL"
        location = Location.Location(get_main_frame().props.uri)
        #location = Location.Location(wnd().props.location)
    return location
    JS("""
    if(!Window_location)
       Window_location = Location_Location($wnd.location);
    return Window_location;
    """)
 
 
def getTitle():
    return doc.props.title

def open(url, name, features):
    JS("""
    $wnd.open(url, name, features);
    """)

def removeWindowCloseListener(listener):
    global closingListeners
    closingListeners.remove(listener)

def removeWindowResizeListener(listener):
    global resizeListeners
    resizeListeners.remove(listener)

def setMargin(size):
    doc().props.body.props.style.margin = size;

def setTitle(title):
    doc().props.title = title

# TODO: call fireClosedAndCatch
def onClosed():
    fireClosedImpl()

# TODO: call fireClosingAndCatch
def onClosing():
    fireClosingImpl()

# TODO: call fireResizedAndCatch
def onResize():
    fireResizedImpl()

def fireClosedAndCatch(handler):
    # FIXME - need implementation
    pass

def fireClosedImpl():
    global closingListeners
    
    for listener in closingListeners:
        listener.onWindowClosed()

def fireClosingAndCatch(handler):
    # FIXME - need implementation
    pass

def fireClosingImpl():
    global closingListeners
    
    ret = None
    for listener in closingListeners:
        msg = listener.onWindowClosing()
        if ret == None:
            ret = msg
    return ret

def fireResizedAndCatch(handler):
    # FIXME - need implementation
    pass

def fireResizedImpl():
    global resizeListeners

    for listener in resizeListeners:
        listener.onWindowResized(getClientWidth(), getClientHeight())

