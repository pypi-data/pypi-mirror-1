# Copyright 2006 James Tauber and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from Window import onResize, onClosing, onClosed
from __pyjamas__ import JS, doc, get_main_frame, wnd

sCaptureElem = None
sEventPreviewStack = []

def _dispatchEvent(evt):
    
    listener = None
    curElem =  evt.props.target
    
    while curElem and not hasattr(curElem, "_listener"):
        curElem = getParent(curElem)
    if curElem and getNodeType(curElem) != 1:
        curElem = None

    if curElem and hasattr(curElem, "_listener") and curElem._listener:
        dispatchEvent(evt, curElem, curElem._listener)
    
def _dispatchCapturedMouseEvent(evt):

    if (_dispatchCapturedEvent(evt)):
        mf = get_main_frame()
        cap = mf._captureElem
        if cap and cap._listener:
            dispatchEvent(evt, cap, cap._listener)
            evt.stop_propagation()

def _dispatchCapturedMouseoutEvent(evt):
    mf = get_main_frame()
    cap = mf._captureElem
    if cap:
        print "cap", dir(evt), cap
        if not eventGetToElement(evt):
            print "synthesise", cap
            #When the mouse leaves the window during capture, release capture
            #and synthesize an 'onlosecapture' event.
            mf._captureElem = None
            if cap._listener:
                # this should be interesting...
                lcEvent = doc().create_event('UIEvent')
                lcEvent.init_ui_event('losecapture', False, False, wnd(), 0)
                dispatchEvent(lcEvent, cap, cap._listener);

def browser_event_cb(view, event, from_window):

    et = eventGetType(event)
    if et == "resize":
        onResize()
        return
    elif et == 'mouseout':
        print "mouse out", event
        _dispatchCapturedMouseoutEvent(event)
    elif et == 'keyup' or et == 'keydown' or et == 'keypress' or et == 'change':
        _dispatchCapturedEvent(event)
    else:
        _dispatchCapturedMouseEvent(event)

def _dispatchCapturedEvent(event):

    if not previewEvent(event):
        event.stop_propagation()
        event.prevent_default()
        return False
    return True

def window_init():

    mf = get_main_frame()
    mf._captureElem = None
    mf.connect("browser-event", browser_event_cb) # yuk.  one signal? oh well..
    mf.add_window_event_listener("click")
    mf.add_window_event_listener("change")
    mf.add_window_event_listener("mouseout")
    mf.add_window_event_listener("mousedown")
    mf.add_window_event_listener("mouseup")
    mf.add_window_event_listener("resize")
    mf.add_window_event_listener("keyup")
    mf.add_window_event_listener("keydown")
    mf.add_window_event_listener("keypress")


def init():

    print "TODO"
    return
    JS("""
    // Set up capture event dispatchers.
    $wnd.__dispatchCapturedMouseEvent = function(evt) {
        if ($wnd.__dispatchCapturedEvent(evt)) {
            var cap = $wnd._captureElem;
            if (cap && cap._listener) {
                DOM_dispatchEvent(evt, cap, cap._listener);
                evt.stopPropagation();
            }
        }
    };

    $wnd.__dispatchCapturedEvent = function(evt) {
        if (!DOM_previewEvent(evt)) {
            evt.stopPropagation();
            evt.preventDefault();
            return false;
        }

        return true;
        };

    $wnd.addEventListener(
        'mouseout',
        function(evt){
            var cap = $wnd._captureElem;
            if (cap) {
                if (!evt.relatedTarget) {
                    // When the mouse leaves the window during capture, release capture
                    // and synthesize an 'onlosecapture' event.
                    $wnd._captureElem = null;
                    if (cap._listener) {
                        var lcEvent = $doc.createEvent('UIEvent');
                        lcEvent.initUIEvent('losecapture', false, false, $wnd, 0);
                        DOM_dispatchEvent(lcEvent, cap, cap._listener);
                    }
                }
            }
        },
        true
    );


    $wnd.addEventListener('click', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('dblclick', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mousedown', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mouseup', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mousemove', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('keydown', $wnd.__dispatchCapturedEvent, true);
    $wnd.addEventListener('keyup', $wnd.__dispatchCapturedEvent, true);
    $wnd.addEventListener('keypress', $wnd.__dispatchCapturedEvent, true);
    
    $wnd.__dispatchEvent = function(evt) {
    
        var listener, curElem = this;
        
        while (curElem && !(listener = curElem._listener)) {
            curElem = curElem.props.parent_node;
        }
        if (curElem && curElem.props.node_type != 1) {
            curElem = null;
        }
    
        if (listener) {
            DOM_dispatchEvent(evt, curElem, listener);
        }
    };
    
    $wnd._captureElem = null;
    """)

init()

def addEventPreview(preview):
    global sEventPreviewStack
    sEventPreviewStack.append(preview)

def appendChild(parent, child):
    print "appendChild", parent, child
    parent.append_child(child)

def compare(elem1, elem2):
    return elem1.is_same_node(elem2)

def createAnchor():
    return createElement("A")

def createButton():
    return createElement("button")

def createCol():
    return createElement("col")

def createDiv():
    return createElement("div")

def createElement(tag):
    return doc().create_element(tag)

def createFieldSet():
    return createElement("fieldset")

def createForm():
    return createElement("form")

def createIFrame():
    return createElement("iframe")

def createImg():
    return createElement("img")

def createInputCheck():
    return createInputElement("checkbox")

def createInputElement(elementType):
    e = createElement("INPUT")
    e.props.type = elementType;
    return e

def createInputPassword():
    return createInputElement("password")

def createInputRadio(group):
    e = createInputElement('radio')
    e.props.name = group
    return e

def createInputText():
    return createInputElement("text")

def createLabel():
    return createElement("label")

def createLegend():
    return createElement("legend")

def createOptions():
    return createElement("options")

def createSelect():
    return createElement("select")

def createSpan():
    return createElement("span")

def createTable():
    return createElement("table")

def createTBody():
    return createElement("tbody")

def createTD():
    return createElement("td")

def createTextArea():
    return createElement("textarea")

def createTH():
    return createElement("th")

def createTR():
    return createElement("tr")

def eventCancelBubble(evt, cancel):
    evt.cancelBubble = cancel

def eventGetAltKey(evt):
    return evt.props.alt_key

def eventGetButton(evt):
    return evt.props.button

def eventGetClientX(evt):
    return evt.props.client_x

def eventGetClientY(evt):
    return evt.props.client_y

def eventGetCtrlKey(evt):
    return evt.props.ctrl_key

def eventGetFromElement(evt):
    return evt.props.from_element

def eventGetKeyCode(evt):
    return evt.props.which and evt.props.key_code

def eventGetRepeat(evt):
    return evt.props.repeat

def eventGetScreenX(evt):
    return evt.props.screen_x

def eventGetScreenY(evt):
    return evt.props.screen_y

def eventGetShiftKey(evt):
    return evt.props.shift_key

def eventGetTarget(event):
    return event.props.target

def eventGetToElement(evt):
    return evt.props.related_target
    JS("""
    return evt.relatedTarget ? evt.relatedTarget : null;
    """)

def eventGetType(event):
    return event.props.type

def eventGetTypeInt(event):
    JS("""
    switch (event.type) {
      case "blur": return 0x01000;
      case "change": return 0x00400;
      case "click": return 0x00001;
      case "dblclick": return 0x00002;
      case "focus": return 0x00800;
      case "keydown": return 0x00080;
      case "keypress": return 0x00100;
      case "keyup": return 0x00200;
      case "load": return 0x08000;
      case "losecapture": return 0x02000;
      case "mousedown": return 0x00004;
      case "mousemove": return 0x00040;
      case "mouseout": return 0x00020;
      case "mouseover": return 0x00010;
      case "mouseup": return 0x00008;
      case "scroll": return 0x04000;
      case "error": return 0x10000;
    }
    """)

def eventGetTypeString(event):
    return eventGetType(event)

def eventPreventDefault(evt):
    evt.prevent_default()

def eventSetKeyCode(evt, key):
    evt.props.key_code = key

def eventToString(evt):
    return evt.to_strign

def iframeGetSrc(elem):
    return elem.props.src

def getAbsoluteLeft(elem):
    left = 0
    while elem:
        left += elem.props.offset_left - elem.props.scroll_left;
        parent = elem.props.offset_parent;
        if parent and parent.props.tag_name == 'BODY' and \
            hasattr(elem, 'style') and \
            getStyleAttribute(elem, 'position') == 'absolute':
            break
        elem = parent
    
    return left + doc().props.body.props.scroll_left;

def getAbsoluteTop(elem):
    top = 0
    while elem:
        top += elem.props.offset_top - elem.props.scroll_top;
        parent = elem.props.offset_parent;
        if parent and parent.props.tag_name == 'BODY' and \
            hasattr(elem, 'style') and \
            getStyleAttribute(elem, 'position') == 'absolute':
            break
        elem = parent
    
    return top + doc().props.body.props.scroll_top;

def getAttribute(elem, attr):
    return str(elem.get_property(mash_name_for_glib(attr)))

def getElemAttribute(elem, attr):
    if not elem.has_attribute(attr):
        return str(elem.get_property(mash_name_for_glib(attr)))
    return str(elem.get_attribute(attr))

def getBooleanAttribute(elem, attr):
    return bool(elem.get_property(mash_name_for_glib(attr)))

def getBooleanElemAttribute(elem, attr):
    if not elem.has_attribute(attr):
        return None
    return bool(elem.get_attribute(attr))

def getCaptureElement():
    global sCaptureElem
    return sCaptureElem

def getChild(elem, index):
    """
    Get a child of the DOM element by specifying an index.
    """
    count = 0
    child = elem.props.first_child
    while child:
        next = child.props.next_sibling;
        if child.props.node_type == 1:
            if index == count:
              return child;
            count += 1
        child = next
    return None

def getChildCount(elem):
    """
    Calculate the number of children the given element has.  This loops
    over all the children of that element and counts them.
    """
    count = 0
    child = elem.props.first_child;
    while child:
      if child.props.node_type == 1:
          count += 1
      child = child.props.next_sibling;
    return count;

def getChildIndex(parent, toFind):
    """
    Return the index of the given child in the given parent.
    
    This performs a linear search.
    """
    count = 0
    child = parent.props.first_child;
    while child:
        if child == toFind:
            return count
        if child.props.node_type == 1:
            count += 1
        child = child.props.next_sibling

    return -1;

def getElementById(id):
    """
    Return the element in the document's DOM tree with the given id.
    """
    return doc().get_element_by_id(id)

def getEventListener(element):
    """
    See setEventListener for more information.
    """
    return element._listener

def getEventsSunk(element):
    print "TODO"
    return 0
    """
    Return which events are currently "sunk" for a given DOM node.  See
    sinkEvents() for more information.
    """
    JS("""
    return element.__eventBits ? element.__eventBits : 0;
    """)

def getFirstChild(elem):
    child = elem and elem.props.first_child
    while child and child.props.node_type != 1:
        child = child.props.next_sibling
    return child

def getInnerHTML(element):
    return element and element.props.inner_html

def getInnerText(element):
    # To mimic IE's 'innerText' property in the W3C DOM, we need to recursively
    # concatenate all child text nodes (depth first).
    text = ''
    child = element.props.first_child;
    while child:
      if child.props.node_type == 1:
        text += child.get_inner_text()
      elif child.props.node_value:
        text += child.props.node_value
      child = child.props.next_sibling
    return text

def getIntAttribute(elem, attr):
    return int(elem.get_property(mash_name_for_glib(attr)))

def getIntElemAttribute(elem, attr):
    if not elem.has_attribute(attr):
        return None
    return int(elem.get_attribute(attr))

def getIntStyleAttribute(elem, attr):
    return int(elem.style.get_property(mash_name_for_glib(attr)))

def getNextSibling(elem):
    sib = elem.props.next_sibling
    while sib and sib.props.node_type != 1:
        sib = sib.props.next_sibling
    return sib

def getNodeType(elem):
    return elem.props.node_type 

def getParent(elem):
    parent = elem.props.parent_node 
    if parent is None:
        return None
    if getNodeType(parent) != 1:
        return None
    return parent 

def getStyleAttribute(elem, attr):
    return elem.style.get_property(mash_name_for_glib(attr))

def insertChild(parent, toAdd, index):
    count = 0
    child = parent.props.first_child
    before = None;
    while child:
        if child.props.node_type == 1:
            if (count == index):
                before = child;
                break
            
            count += 1
        child = child.props.next_sibling

    if before is None:
        parent.append_child(toAdd)
    else:
        parent.insert_before(toAdd, before)

def iterChildren(elem):
    """
    Returns an iterator over all the children of the given
    DOM node.
    """
    JS("""
    var parent = elem;
    var child = elem.props.first_child;
    var lastChild = null;
    return {
        'next': function() {
            if (child == null) {
                throw StopIteration;
            }
            lastChild = child;
            child = DOM_getNextSibling(child);
            return lastChild;
        },
        'remove': function() {        
            parent.removeChild(lastChild);
        },
        __iter__: function() {
            return this;
        }
    };
    """)

def walkChildren(elem):
    """
    Walk an entire subtree of the DOM.  This returns an
    iterator/iterable which performs a pre-order traversal
    of all the children of the given element.
    """
    JS("""
    var parent = elem;
    var child = DOM_getFirstChild(elem);
    var lastChild = null;
    var stack = [];
    var parentStack = [];
    return {
        'next': function() {
            if (child == null) {
                throw StopIteration;
            }
            lastChild = child;
            var props.first_child = DOM_getFirstChild(child);
            var props.next_sibling = DOM_getNextSibling(child);
            if(props.first_child != null) {
               if(props.next_sibling != null) {
                   stack.push(props.next_sibling);
                   parentStack.push(parent);
                }
                parent = child;
                child = props.first_child;
            } else if(props.next_sibling != null) {
                child = props.next_sibling;
            } else if(stack.length > 0) {
                child = stack.pop();
                parent = parentStack.pop();
            } else {
                child = null;
            }
            return lastChild;
        },
        'remove': function() {        
            parent.removeChild(lastChild);
        },
        __iter__: function() {
            return this;
        }
    };
    """)
   
def isOrHasChild(parent, child):
    while child:
        if parent == child:
            return True
        child = child.props.parent_node;
        if not child:
            return False
        if child.props.node_type != 1:
            child = None
    return False

def releaseCapture(elem):
    global sCaptureElem
    if sCaptureElem and compare(elem, sCaptureElem):
        sCaptureElem = None
    return
    JS("""
    if ((DOM_sCaptureElem != null) && DOM_compare(elem, DOM_sCaptureElem))
        DOM_sCaptureElem = null;

    if (elem == $wnd._captureElem)
        $wnd._captureElem = null;
    """)

def removeChild(parent, child):
    parent.remove_child(child)

def replaceChild(parent, newChild, oldChild):
    parent.replace_child(newChild, oldChild)

def removeEventPreview(preview):
    global sEventPreviewStack
    sEventPreviewStack.remove(preview)

def scrollIntoView(elem):
    JS("""
    var left = elem.offsetLeft, top = elem.offsetTop;
    var width = elem.offsetWidth, height = elem.offsetHeight;
    
    if (elem.props.parent_node != elem.offsetParent) {
        left -= elem.props.parent_node.offsetLeft;
        top -= elem.props.parent_node.offsetTop;
    }

    var cur = elem.props.parent_node;
    while (cur && (cur.props.node_type == 1)) {
        if ((cur.style.overflow == 'auto') || (cur.style.overflow == 'scroll')) {
            if (left < cur.scrollLeft) {
                cur.scrollLeft = left;
            }
            if (left + width > cur.scrollLeft + cur.clientWidth) {
                cur.scrollLeft = (left + width) - cur.clientWidth;
            }
            if (top < cur.scrollTop) {
                cur.scrollTop = top;
            }
            if (top + height > cur.scrollTop + cur.clientHeight) {
                cur.scrollTop = (top + height) - cur.clientHeight;
            }
        }

        var offsetLeft = cur.offsetLeft, offsetTop = cur.offsetTop;
        if (cur.props.parent_node != cur.offsetParent) {
            offsetLeft -= cur.props.parent_node.offsetLeft;
            offsetTop -= cur.props.parent_node.offsetTop;
        }

        left += offsetLeft - cur.scrollLeft;
        top += offsetTop - cur.scrollTop;
        cur = cur.props.parent_node;
    }
    """)

def mash_name_for_glib(name):
    res = ''
    for c in name:
        if c.isupper():
            res += "-" + c.lower()
        else:
            res += c
    return res

def removeAttribute(element, attribute):
    elem.remove_attribute(attribute)

def setAttribute(element, attribute, value):
    element.set_property(mash_name_for_glib(attribute), value)

def setElemAttribute(element, attribute, value):
    element.set_attribute(attribute, value)

def setBooleanAttribute(elem, attr, value):
    elem.set_property(mash_name_for_glib(attr), value)

def setCapture(elem):
    global sCaptureElem
    sCaptureElem = elem
    mf = get_main_frame()
    mf._captureElem = elem
    JS("""
    DOM_sCaptureElem = elem;
    $wnd._captureElem = elem;
    """)

def setEventListener(element, listener):
    """
    Register an object to receive event notifications for the given
    element.  The listener's onBrowserEvent() method will be called
    when a captured event occurs.  To set which events are captured,
    use sinkEvents().
    """
    element._listener = listener

def setInnerHTML(element, html):
    element.props.inner_html = html

def setInnerText(elem, text):
    #Remove all children first.
    while elem.props.first_child:
        elem.remove_child(elem.props.first_child)
    elem.append_child(doc().create_text_node(text or ''))

def setIntElemAttribute(elem, attr, value):
    elem.set_attribute(attr, str(value))

def setIntAttribute(elem, attr, value):
    elem.set_property(mash_name_for_glib(attr), value)

def setIntStyleAttribute(elem, attr, value):
    sty = elem.props.style
    sty.set_css_property(attr, str(value), "")

def setOptionText(select, text, index):
    print "TODO - setOptionText"
    JS("""
    var option = select.options[index];
    option.text = text;
    """)

def setStyleAttribute(element, name, value):
    sty = element.props.style
    sty.set_css_property(name, value, "")

def dispatch_event_cb(element, event, capture):
    print "dispatch_event_cb", element, event, capture

def sinkEvents(element, bits):
    """
    Set which events should be captured on a given element and passed to the
    registered listener.  To set the listener, use setEventListener().
    
    @param bits: A combination of bits; see ui.Event for bit values
    """
    element.__eventBits = bits;
    if bits:
        element.connect("browser-event", lambda x,y,z: _dispatchEvent(y))
    if (bits & 0x00001):
        element.add_event_listener("click", True)
    if (bits & 0x00002):
        element.add_event_listener("dblclick", True)
    if (bits & 0x00004):
        element.add_event_listener("mousedown", True)
    if (bits & 0x00008):
        element.add_event_listener("mouseup", True)
    if (bits & 0x00010):
        element.add_event_listener("mouseover", True)
    if (bits & 0x00020):
        element.add_event_listener("mouseout", True)
    if (bits & 0x00040):
        element.add_event_listener("mousemove", True)
    if (bits & 0x00080):
        element.add_event_listener("keydown", True)
    if (bits & 0x00100):
        element.add_event_listener("keypress", True)
    if (bits & 0x00200):
        element.add_event_listener("keyup", True)
    if (bits & 0x00400):
        element.add_event_listener("change", True)
    if (bits & 0x00800):
        element.add_event_listener("focus", True)
    if (bits & 0x01000):
        element.add_event_listener("blur", True)
    if (bits & 0x02000):
        element.add_event_listener("losecapture", True)
    if (bits & 0x04000):
        element.add_event_listener("scroll", True)
    if (bits & 0x08000):
        element.add_event_listener("load", True)
    if (bits & 0x10000):
        element.add_event_listener("error", True)

def toString(elem):
    temp = elem.clone_node(True)
    tempDiv = createDiv()
    tempDiv.append_child(temp)
    outer = tempDiv.props.inner_html
    temp.props.inner_html = ""
    return outer

# TODO: missing dispatchEventAndCatch
def dispatchEvent(event, element, listener):
    dispatchEventImpl(event, element, listener)

def previewEvent(evt):
    global sEventPreviewStack
    ret = True
    if len(sEventPreviewStack) > 0:
        preview = sEventPreviewStack[len(sEventPreviewStack) - 1]
        
        ret = preview.onEventPreview(evt)
        if not ret:
            eventCancelBubble(evt, True)
            eventPreventDefault(evt)

    return ret

# TODO
def dispatchEventAndCatch(evt, elem, listener, handler):
    pass

def dispatchEventImpl(event, element, listener):
    global sCaptureElem
    if element == sCaptureElem:
        if eventGetType(event) == "losecapture":
            sCaptureElem = None
    listener.onBrowserEvent(event)

def insertListItem(select, item, value, index):
    option = createElement("OPTION")
    setInnerText(option, item)
    if value != None:
        setAttribute(option, "value", value)
    if index == -1:
        appendChild(select, option)
    else:
        insertChild(select, option, index)




