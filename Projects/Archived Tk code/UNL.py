#@+leo-ver=5-thin
#@+node:ekr.20110602070710.3423: * @file UNL.py
#@+<< docstring >>
#@+node:ekr.20110602070710.3424: ** << docstring >>
''' Supports Uniform Node Locators (UNL's) for linking to nodes in any Leo file.

UNL's specify nodes within any Leo file. You can use them to create
cross-Leo-file links! UNL

This plugin consists of two parts:

1) Selecting a node shows the UNL in the status line at the bottom of the Leo
   window. You can copy from the status line and paste it into headlines, emails,
   whatever. 

2) Double-clicking @url nodes containing UNL's select the node specified in the
   UNL. If the UNL species in another Leo file, the other file will be opened.

Format of UNL's:

UNL's referring to nodes within the present outline have the form::

    headline1-->headline2-->...-->headlineN

headline1 is the headline of a top-level node, and each successive headline is
the headline of a child node.

UNL's of the form::

    file:<path>#headline1-->...-->headlineN

refer to a node specified in <path> For example, double clicking the following
headline will take you to Chapter 8 of Leo's Users Guide::

    @url file:c:/prog/leoCvs/leo/doc/leoDocs.leo#Users Guide-->Chapter 8: Customizing Leo

For example, suppose you want to email someone with comments about a Leo file.
Create a comments.leo file containing @url UNL nodes. That is, headlines are
@url followed by a UNL. The body text contains your comments about the nodes in
the _other_ Leo file! Send the comments.leo to your friend, who can use the
comments.leo file to quickly navigate to the various nodes you are talking
about. As another example, you can copy UNL's into emails. The recipient can
navigate to the nodes 'by hand' by following the arrows in the UNL.

**Notes**:

- At present, UNL's refer to nodes by their position in the outline. Moving a
  node will break the link.

- Don't refer to nodes that contain UNL's in the headline. Instead, refer to the
  parent or child of such nodes.

- You don't have to replace spaces in URL's or UNL's by '%20'.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.11"
#@+<< todo >>
#@+node:ekr.20110602070710.3425: ** << todo >>
#@@nocolor-node
#@+at
# 
# How about other plugins that create a status line? Should I test whether the
# status line is already created?
# 
# Don't know exactly yet about the interaction with other plugins. The info in the
# status line may be overwritten by them. That's fine with me: I can always click
# on the icon of the node again to show the info again.
# 
# Keep the pane of the UNL referred to on top (now the pane with the referring
# node stays on top). Maybe this should be a settings-dependent behaviour. Could
# this be solved by using the 'onCreate' idiom and a UNLclass?
# 
# Find out about the difference between the event 'select2' and 'select3'.
# 
# A UNL checker script would be handy to check whether all references are still
# valid.
# 
# Deal with path-separators for various platforms?
# 
# Handle relative paths?
# 
# Introduce a menu item to improve documentation? By firing up a browser,
# directing it to leo on sourceforge (sourceforge userid needed?). EKR could start
# up a new thread beforehand, "documentation improvements", where a new message
# might be posted with the relevant UNL placed automatically in the text box. Then
# the user just needs to type in his/her comments and post the message.
#@-<< todo >>
#@+<< version history >>
#@+node:ekr.20110602070710.3426: ** << version history >>
#@+at
# 
# - 0.1 rogererens: Initial version.
# - 0.2 ekr:  changes for new status line class.
# - 0.3 ekr: Added support for url keyword in '@url1' hook.
#            As a result, this plugin supports single and double quoted urls.
# - 0.4 ekr: Fixed crasher by adding c argument to g.findTopLevelNode and g.findNodeInTree.
# - 0.5 EKR: Convert %20 to ' ' in url's.
# - 0.6 EKR: Made local UNL's work.
# - 0.7 EKR: Set c.doubleClickFlag to keep focus in newly-opened window.
# - 0.8 johnmwhite: Patch to onURl1 to handle @url file: headlines properly.
# - 0.9 EKR: Fixed bug reported by Terry Brown:
#     Replaced calls to findNodeInTree by findNodeInChildren.
# - 0.10 TB: Added recursive search so that the longest match will be found.
# - 0.11 EKR: This gui is now gui-independent.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20110602070710.3427: ** << imports >>
import leo.core.leoGlobals as g

import os

if g.isPython3:
    import urllib.parse as urlparse
else:
    import urlparse 
#@-<< imports >>
#@+<< globals >>
#@+node:ekr.20110602070710.3428: ** << globals >>
#@+at
# 
#@-<< globals >>

#@+others
#@+node:ekr.20110602070710.3429: ** init
def init ():

    #if g.app.gui is None:
    #    g.app.createTkGui(__file__)

    g.registerHandler("after-create-leo-frame", createStatusLine)
    g.registerHandler("select2", onSelect2) # show UNL
    g.registerHandler("@url1", onUrl1) # jump to URL or UNL

    g.plugin_signon(__name__)
    return True
#@+node:ekr.20110602070710.3430: ** createStatusLine
def createStatusLine(tag,keywords):

    """Create a status line.""" # Might already be done by another plugin. Checking needed?

    c = keywords.get("c")
    statusLine = c.frame.createStatusLine()
    statusLine.clear()
    statusLine.put("...")
#@+node:ekr.20110602070710.3431: ** recursiveUNLSearch
def recursiveUNLSearch(unlList, c, depth=0, p=None, maxdepth=0, maxp=None):
    """try and move to unl in the commander c
    
    NOTE: maxdepth is max depth seen in recursion so far, not a limit on
          how fast we will recurse.  So it should default to 0 (zero).
    """

    def moveToP(c, p):
        c.expandAllAncestors(p) # 2009/11/07
        c.selectPosition(p)
        c.redraw()
        c.frame.bringToFront()  # doesn't seem to work

    if depth == 0:
        nds = c.rootPosition().self_and_siblings()
    else:
        nds = p.children()

    for i in nds:

        if unlList[depth] == i.h:

            if depth+1 == len(unlList):  # found it
                moveToP(c, i)
                return True, maxdepth, maxp
            else:
                if maxdepth < depth+1:
                    maxdepth = depth+1
                    maxp = i.copy()
                found, maxdepth, maxp = recursiveUNLSearch(unlList, c, depth+1, i, maxdepth, maxp)
                if found:
                    return found, maxdepth, maxp
                # else keep looking through nds

    if depth == 0 and maxp:  # inexact match
        moveToP(c, maxp)
        g.es('Partial UNL match')

    return False, maxdepth, maxp
#@+node:ekr.20110602070710.3432: ** onUrl1
def onUrl1 (tag,keywords):
    """Redefine the @url functionality of Leo Core: allows jumping to URL _and UNLs_.
    Spaces are now allowed in URLs."""
    trace = False and not g.unitTesting
    c = keywords.get("c")
    p = keywords.get("p")
    v = keywords.get("v")
    # The url key is new in 4.3 beta 2.
    # The url ends with the first blank, unless either single or double quotes are used.
    url = keywords.get('url') or ''
    url = url.replace('%20',' ')

#@+at Most browsers should handle the following urls:
#   ftp://ftp.uu.net/public/whatever.
#   http://localhost/MySiteUnderDevelopment/index.html
#   file://home/me/todolist.html
#@@c
    try:
        try:
            urlTuple = urlparse.urlsplit(url)
            if trace: logUrl(urlTuple)
        except:
            g.es("exception interpreting the url " + url)
            g.es_exception()
            return False

        if not urlTuple[0]:
            urlProtocol = "file" # assume this protocol by default
        else:
            urlProtocol = urlTuple[0]

        if urlProtocol == "file":
            if urlTuple[2].endswith(".leo"):
                if hasattr(c.frame.top, 'update_idletasks'):
                    # this is Tk only - TNB
                    c.frame.top.update_idletasks()
                        # Clear remaining events, so they don't interfere.
                filename = os.path.expanduser(urlTuple[2])
                filename = g.os_path_expandExpression(filename,c=c)
                    # 2011/01/25: bogomil
    
                if not os.path.isabs(filename):
                    filename = os.path.normpath(os.path.join(c.getNodePath(p),filename))

                ok,frame = g.openWithFileName(filename, c)
                if ok:
                    #@+<< go to the node>>
                    #@+node:ekr.20110602070710.3433: *3* <<go to the node>>
                    c2 = frame.c

                    if urlTuple [4]: # we have a UNL!
                        recursiveUNLSearch(urlTuple[4].split("-->"), c2)

                    # Disable later call to c.onClick so the focus stays in c2.
                    c.doubleClickFlag = True
                    #@-<< go to the node>>
            elif urlTuple[0] == "":
                #@+<< go to node in present outline >>
                #@+node:ekr.20110602070710.3434: *3* << go to node in present outline >>
                if urlTuple [2]:
                    recursiveUNLSearch(urlTuple[2].split("-->"), c)
                #@-<< go to node in present outline >>
            else:
                #@+<<invoke external browser>>
                #@+node:ekr.20110602070710.3435: *3* <<invoke external browser>>
                import webbrowser

                # Mozilla throws a weird exception, then opens the file!
                try:
                    webbrowser.open(url)
                except:
                    pass
                #@-<<invoke external browser>>
        else:
            #@+<<invoke external browser>>
            #@+node:ekr.20110602070710.3435: *3* <<invoke external browser>>
            import webbrowser

            # Mozilla throws a weird exception, then opens the file!
            try:
                webbrowser.open(url)
            except:
                pass
            #@-<<invoke external browser>>
        return True
            # PREVENTS THE EXECUTION OF LEO'S CORE CODE IN
            # Code-->Gui Base classes-->@thin leoFrame.py-->class leoTree-->tree.OnIconDoubleClick (@url)
    except:
        g.es("exception opening " + url)
        g.es_exception()
        return False
#@+node:ekr.20110602070710.3436: *3* logUrl
def logUrl(urlTuple):

    g.trace("scheme  : " + urlTuple[0])
    g.trace("network : " + urlTuple[1])
    g.trace("path    : " + urlTuple[2])
    g.trace("query   : " + urlTuple[3])
    g.trace("fragment: " + urlTuple[4])
#@+node:ekr.20110602070710.3437: ** onSelect2
def onSelect2 (tag,keywords):

    """Shows the UNL in the status line whenever a node gets selected."""

    c = keywords.get("c")

    # c.p is not valid while using the settings panel.
    new_p = keywords.get('new_p')
    if not new_p: return    

    c.frame.clearStatusLine()
    myList = [p.h for p in new_p.self_and_parents()]
    myList.reverse()

    # Rich has reported using ::
    # Any suggestions for standardization?
    s = "-->".join(myList)
    c.frame.putStatusLine(s)
#@-others
#@-leo
