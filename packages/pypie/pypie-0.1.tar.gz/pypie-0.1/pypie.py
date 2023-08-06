#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4

import os, sys, re, logging
from functools import wraps, partial
from optparse import OptionParser
import gtk, gobject
from gtk import gdk
import wnck

__doc__ = """
#.rules.py example

#@opened(name='gvim')
#def move_gvim(win):
#    " resize and move gvim when it's started "
#    win.move(0,54)
#    win.resize(1124,689)

#@opened(app_name='chromium-browser')
#def maximize_chrominum(win):
#    win.maximize()

#@moved(name='gvim')
#def gvim_moved(win):
#    " print gvim position when it's moved "
#    print win.get_position()

#@opened(name='Buddy List')
#def fix_pidgin(window):
#    " fix pidgin window in the right corner "
#    window.move(1072, 0)
#    window.resize(208, 745)
#    #window.set_functions(gdk.FUNC_ALL ^ gdk.FUNC_MOVE ^ gdk.FUNC_RESIZE)
#    window.set_functions(gdk.FUNC_CLOSE)

#@focused(app_name='mplayer')
#def mplayer_tomon1(window):
#    " move mplayer to second monitor "
#    window.to_monitor(1)
#    window.fullscreen()
"""

#class Window(object):
#    def __init__(self, w):
#        gw = gdk.window_foreign_new(w.get_xid())
#        for k,v in w.__class__.__dict__.items():
#            if callable(v) and not k.startswith('_'):
#                setattr(self, k, partial(v, w))
#        for k,v in gw.__class__.__dict__.items():
#            if callable(v) and not k.startswith('_'):
#                setattr(self, k, partial(v, gw))
#STATE_NORMAL = 0
#STATE_MINIMIZED = 129
#STATE_MAXIMIZED = 6
#STATE_FULLSCREEN = 256

class Window(object):
    """
    own methods:
    to_monitor
    methods from wnck.Window:
    activate activate_transient close get_actions get_application get_class_group get_client_window_geometry get_geometry get_group_leader get_icon get_icon_is_fallback get_icon_name get_mini_icon get_name get_pid get_screen get_session_id get_session_id_utf8 get_sort_order get_state get_transient get_window_type get_workspace get_xid has_icon_name has_name is_above is_active is_below is_fullscreen is_in_viewport is_maximized is_maximized_horizontally is_maximized_vertically is_minimized is_most_recently_activated is_on_workspace is_pinned is_shaded is_skip_pager is_skip_tasklist is_sticky is_visible_on_workspace keyboard_move keyboard_size make_above make_below maximize maximize_horizontally maximize_vertically minimize move_to_workspace needs_attention or_transient_needs_attention pin set_fullscreen set_geometry set_icon_geometry set_skip_pager set_skip_tasklist set_sort_order set_window_type shade stick transient_is_most_recently_activated unmake_above unmake_below unmaximize unmaximize_horizontally unmaximize_vertically unminimize unpin unshade unstick
    methods from gtk.gdk.Window:
    add_filter beep begin_move_drag begin_paint_rect begin_paint_region begin_resize_drag clear clear_area clear_area_e configure_finished deiconify destroy destroy_notify drag_begin enable_synchronized_configure end_paint focus freeze_updates fullscreen get_children get_decorations get_deskrelative_origin get_events get_frame_extents get_geometry get_group get_origin get_parent get_pointer get_position get_root_origin get_state get_toplevel get_type_hint get_update_area get_user_data get_window_type hide iconify input_set_extension_events input_shape_combine_mask input_shape_combine_region invalidate_rect invalidate_region is_viewable is_visible lower maximize merge_child_input_shapes merge_child_shapes move move_region move_resize move_to_current_desktop process_updates property_change property_delete property_get raise_ redirect_to_drawable register_dnd remove_redirection reparent resize scroll selection_convert set_accept_focus set_back_pixmap set_background set_child_input_shapes set_child_shapes set_composited set_cursor set_decorations set_events set_focus_on_map set_functions set_geometry_hints set_group set_hints set_icon set_icon_list set_icon_name set_keep_above set_keep_below set_modal_hint set_opacity set_override_redirect set_role set_skip_pager_hint set_skip_taskbar_hint set_startup_id set_static_gravities set_title set_transient_for set_type_hint set_urgency_hint set_user_data set_user_time shape_combine_mask shape_combine_region show show_unraised stick thaw_updates unfullscreen unmaximize unstick withdraw
    """

    def __init__(self, wnck_window):
        self.wnck_window = wnck_window
        self.gdk_window = gdk.window_foreign_new(wnck_window.get_xid())

    def __getattr__(self, k):
        if k in ['above', 'active', 'below', 'fullscreen', 'maximized', 'maximized_horizontally', 'maximized_vertically', 'minimized', 'most_recently_activated', 'pinned', 'shaded', 'skip_pager', 'skip_tasklist', 'sticky']:
            return getattr(self.wnck_window,'is_%s' % k)()
        if k in ['geometry', 'state', 'pid', 'xid', 'actions', 'window_type', 'client_window_geometry', 'name']:
            return getattr(self.wnck_window,'get_%s' % k)()
        if k in ['decorations', 'frame_extents', 'geometry', 'origin', 'position', 'root_origin', 'size', 'type_hint', 'window_type']:
            return getattr(self.gdk_window,'get_%s' % k)()
        
        if hasattr(self.wnck_window, k):
            return getattr(self.wnck_window, k)
        elif hasattr(self.gdk_window, k):
            return getattr(self.gdk_window, k)
        else:
            raise AttributeError("Window has no attribute '%s'" % k)

    def __dir__(self):
        return [k for k in dir(wnck.Window)+dir(gdk.Window) if not k.startswith('_')]+dir(Window)

    def to_monitor(self, monitor_number):
        was_max = self.wnck_window.is_maximized()
        was_fs = self.wnck_window.is_fullscreen()
        self.wnck_window.unmaximize()
        self.wnck_window.set_fullscreen(False)
        s = self.gdk_window.get_screen()
        cur = s.get_monitor_at_window(self.gdk_window)
        if cur == monitor_number:
            return
        mong = s.get_monitor_geometry(monitor_number)
        curmong = s.get_monitor_geometry(cur)
        pos = list(self.gdk_window.get_root_origin())
        pos[0] += mong[0] - curmong[0]
        pos[1] += mong[1] - curmong[1]
        self.gdk_window.move(*pos)
        if was_max:
            self.wnck_window.maximize()
        self.wnck_window.set_fullscreen(was_fs)
    
    def focus(self):
        self.wnck_window.activate(int(gobject.get_current_time()))

    @property
    def name(self):
        return self.wnck_window.get_name()


#def _event_decorator(event_name, event, f):
#    screen.connect(event, f)
#    f.event = event_name
#    if event_name not in connected:
#        connected[event_name] = []
#    connected[event_name].append(f)
#    return f

def _event_decorator(event_name, event, **kargs):
    def wrap(f):
        for _name, _func in functions:
            if _name in kargs:
                f = _decorator(_func, _name, kargs[_name])(f)
        screen.connect(event, f)
        f.event = event_name
        if event_name not in connected:
            connected[event_name] = []
        connected[event_name].append(f)
        return f
    wrap.event = event_name
    return wrap

#def _window_event(event_name, event, f):
#    f.event = event_name

#    if event_name not in connected:
#        connected[event_name] = []
#    connected[event_name].append(f)
#    return f

def _window_event(event_name, event, **kargs):
    def wrap(f):
        for _name, _func in functions:
            if _name in kargs:
                f = _decorator(_func, _name, kargs[_name])(f)
        f.event = event_name
        if event_name not in connected:
            connected[event_name] = []
        connected[event_name].append(f)
        return f
    wrap.event = event_name
    return wrap



def _decorator(attr, attr_title, match):
    src = repr(match)
    if isinstance(match, basestring):
        match = re.compile('.*%s.*' % match, re.IGNORECASE).match
    elif hasattr(match, 'match'):
        match = match.match
    def dec(f):
        @wraps(f)
        def wrap(w, *args):
            if isinstance(w, wnck.Screen):
                args = list(args)
                w = args.pop(0)
            if wrap.event == 'focused':
                w = screen.get_active_window()
            if match(attr(w)):
                if opts.verbose:
                    print wrap.event, attr_title, repr(attr(w)), 'match', src, 'function: %r' % f.__name__
                return f(Window(w), *args)
            return True
        wrap.src = src
        #wrap.match = match
        #wrap.attr = attr
        return wrap
    return dec

screen_events = (
    ('focused', 'active-window-changed'),
    ('opened', 'window-opened'),
    #('app_opened', 'application-opened'),
)
window_events = (
    ('moved', 'geometry-changed'),
    ('state_changed', 'state-changed'),
    ('workspace_changed', 'workspace-changed'),
    ('actions_changed', 'actions-changed'),
)

functions = (
    ('name', lambda w: w and w.get_name() or ''),
    #('icon_name', lambda w: w.get_icon_name()),
    ('app_name', lambda w: w and w.get_application() and w.get_application().get_name() or ''),
    #('app_icon_name', lambda w: w.get_application() and w.get_application().get_icon_name() or ''),
)

for _name, _func in functions:
    globals()[_name] = partial(_decorator, _func, _name)
    
for _name, _event in screen_events:
    globals()[_name] = partial(_event_decorator, _name, _event)

for _name, _event in window_events:
    globals()[_name] = partial(_window_event, _name, _event)

#|  Signals from WnckScreen:
#|    window-manager-changed ()
#|    active-workspace-changed (WnckWorkspace)
#|    window-stacking-changed ()
#|    window-closed (WnckWindow)
#|    workspace-created (WnckWorkspace)
#|    workspace-destroyed (WnckWorkspace)
#|    application-opened (WnckApplication)
#|    application-closed (WnckApplication)
#|    class-group-opened (WnckClassGroup)
#|    class-group-closed (WnckClassGroup)
#|    background-changed ()
#|    showing-desktop-changed ()
#|    viewports-changed ()
#|  Signals from WnckWindow:
#|    name-changed ()
#|    workspace-changed ()
#|    icon-changed ()

def connect_to_window(scr, window):
    for _name, _event in window_events:
        for v in connected.get(_name, []):
            window.connect(_event, v)

def connect_to_windows():
    screen.connect('window-opened', connect_to_window)

def setup_debug():
    def get_debug():
        def debug(s, w):
            if debug.event == 'focused':
                w = s.get_active_window()
            if w:
                print '[%s]' % debug.event, ' '.join('%s: %r' % (_name, _func(w)) for _name, _func in functions)
                print '', ' '.join('%s:%r' % (_name, getattr(w,'get_%s' % _name)()) for _name in \
                    ('geometry', 'client_window_geometry', 'pid', 'xid', 'window_type'))
            return True
        return debug
    debug_focused = focused()(get_debug())
    debug_opened = opened()(get_debug())


if __name__ == '__main__':

    connected = {}
    screen = wnck.screen_get_default()

    opts = OptionParser()
    opts.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
    opts.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="print all events and window information to stdout")
    opts.add_option("-f", "--file",
                  dest="filename", default='~/.rules.py',
                  help="read rules from file(default: ~/.rules.py)")
    opts, args = opts.parse_args()
    
    default_path = opts.filename == '~/.rules.py'
    opts.filename = os.path.expanduser(opts.filename)
    if not os.path.exists(opts.filename):
        print >>sys.stderr, "%s not found" % opts.filename
        if default_path:
            open(opts.filename, "w").write(__doc__)
            print >>sys.stderr, "%s was created, check it out" % opts.filename
        sys.exit(1)
    exec(compile(open(opts.filename).read(),'rules','exec'))

    if opts.verbose:
        for k,v in connected.items():
            print '%s:' % k
            for _func in v:
                print '',getattr(_func,'src','*'),_func
    
    if opts.debug:
        setup_debug()

    if not connected:
        print >>sys.stderr, "no rules defined in %s" % opts.filename
        sys.exit(1)
    connect_to_windows()

    gtk.main()


