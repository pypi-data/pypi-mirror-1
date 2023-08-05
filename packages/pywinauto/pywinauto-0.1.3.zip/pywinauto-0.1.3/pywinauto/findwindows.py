# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"""Provides functions for iterating and finding windows

"""

__revision__ = "$Revision: 189 $"

import re

import ctypes

import win32functions
import win32structures
import handleprops


# currently commented out as finding the best match control
# requires that we know the Friendly class name - which is only
# known by the control wrappers - and I would prefer to keep
# this module from having that dependency.
#import findbestmatch

#=========================================================================
class WindowNotFoundError(Exception):
    "No window could be found"
    pass

#=========================================================================
class WindowAmbiguousError(Exception):
    "There was more then one window that matched"
    pass



#=========================================================================
def find_window(**kwargs):
    """Call findwindows and ensure that only one window is returned

    Calls find_windows with exactly the same arguments as it is called with
    so please see find_windows for a description of them."""
    windows = find_windows(**kwargs)

    if not windows:
        raise WindowNotFoundError()

    if len(windows) > 1:
        raise WindowAmbiguousError(
            "There are %d windows that match the criteria %s"% (
            len(windows),
            str(kwargs),
            )
        )

    return windows[0]

#=========================================================================
def find_windows(class_name = None,
                class_name_re = None,
                parent = None,
                process = None,
                title = None,
                title_re = None,
                top_level_only = True,
                visible_only = True,
                enabled_only = True,
                #best_match = None
    ):
    """Find windows based on criteria passed in

    Possible values are:

    :class_name:  Windows with this window class
    :class_name_re:  Windows whose class match this regular expression
    :parent:    Windows that are children of this
    :process:   Windows running in this process
    :title:     Windows with this Text
    :title_re:  Windows whose Text match this regular expression
    :top_level_only: Top level windows only (default=True)
    :visible_only:   Visible windows only (default=True)
    :enabled_only:   Enabled windows only (default=True)
    """



    if top_level_only:
        # find the top level windows
        windows = enum_windows()

        # if we have been given a parent
        if parent:
            windows = [win for win in windows
                if handleprops.parent(win) == parent]

    else:
        # if not given a parent - and not looking for top level windows
        # look for all children of the desktop
        if not parent:
            parent = win32functions.GetDesktopWindow()

        # look for all children of that parent
        windows = enum_child_windows(parent)

    if class_name and windows:
        windows = [win for win in windows
            if class_name == handleprops.classname(win)]

    if class_name_re and windows:
        windows = [win for win in windows
            if re.match(class_name_re, handleprops.classname(win))]

    if process and windows:
        windows = [win for win in windows
            if handleprops.processid(win) == process]


    if title and windows:
        windows = [win for win in windows
            if title == handleprops.text(win)]

    elif title_re and windows:
        windows = [win for win in windows
            if re.match(title_re, handleprops.text(win))]

#	elif best_match and windows:
#		windows = [findbestmatch.find_best_control_match(best_match, wins),]

    if visible_only and windows:
        windows = [win for win in windows if handleprops.isvisible(win)]

    if enabled_only and windows:
        windows = [win for win in windows if handleprops.isenabled(win)]


    return windows

#=========================================================================
def enum_windows():
    "Return a list of handles of all the top level windows"
    windows = []

    # The callback function that will be called for each HWND
    # all we do is append the wrapped handle
    def enum_win_proc(hwnd, lparam):
        "Called for each window - adds handles to a list"
        windows.append(hwnd)
        return True

    # define the type of the child procedure
    EnumWindowProc = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_long, ctypes.c_long)

    # 'construct' the callback with our function
    proc = EnumWindowProc(enum_win_proc)

    # loop over all the children (callback called for each)
    win32functions.EnumWindows(proc, 0)

    # return the collected wrapped windows
    return windows


#=========================================================================
def enum_child_windows(handle):
    "Return a list of handles of the child windows of this handle"

    # this will be filled in the callback function
    childWindows = []

    # callback function for EnumChildWindows
    def enumChildProc(hWnd, lparam):
        "Called for each child - adds child hwnd to list"

        # append it to our list
        childWindows.append(hWnd)

        # return true to keep going
        return True

    # define the child proc type
    EnumChildProc = ctypes.WINFUNCTYPE(
        ctypes.c_int, 			# return type
        win32structures.HWND, 	# the window handle
        win32structures.LPARAM)	# extra information

    proc = EnumChildProc(enumChildProc)

    # loop over all the children (callback called for each)
    win32functions.EnumChildWindows(handle, proc, 0)

    return childWindows


#=========================================================================
def _unittests():
    "Do a quick test of finding some windows"
    windows = find_windows(
        class_name_re = "#32770",
        enabled_only = False,
        visible_only = False)

    for win in windows:
        print "==" * 20
        print handleprops.dumpwindow(win)



if __name__ == "__main__":
    _unittests()