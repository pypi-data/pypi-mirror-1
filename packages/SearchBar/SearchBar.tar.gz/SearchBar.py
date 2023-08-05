"""SearchBar.py - An IDLE extension for searching for text in windows.

The interface is a small bar which appears on the bottom of the window. The
search bar is closed when the user hits Escape or when the bar loses focus,
e.g. the user clicks elsewhere. (Tab traversal outside the search bar is
disabled.)

This extension implements the usual search options, regular expressions, and
incremental searching. Also, while searching, all matches are highlighted.

Incremental searching can be toggled on/off in the extensions configuration.

"""

import string
import re

import Tkinter
from Tkconstants import TOP, BOTTOM, LEFT, RIGHT, X, NONE

from configHandler import idleConf

import SearchEngine
import WindowSearchEngine


class SearchBar:
    menudefs = []
    def __init__(self, editwin):
        self.fb = find_bar = FindBar(editwin, editwin.status_bar)
        self.rb = replace_bar = ReplaceBar(editwin, editwin.status_bar)

        editwin.text.bind("<<find>>",
                          find_bar.show_findbar_event)
        editwin.text.bind("<<find-again>>",
                          find_bar.search_again_event)
        editwin.text.bind("<<find-selection>>",
                          find_bar.search_selection_event)
        editwin.text.bind("<<replace>>",
                          replace_bar.show_findbar_event)


def FindBar(editwin, pack_after):
    return SearchBarWidget(editwin, pack_after, is_replace=False)
def ReplaceBar(editwin, pack_after):
    return SearchBarWidget(editwin, pack_after, is_replace=True)

class SearchBarWidget:
    def __init__(self, editwin, pack_after, is_replace=False):
        self.text = editwin.text
        self.root = self.text._root()
        self.engine = SearchEngine.get(self.root)
        self.window_engine = WindowSearchEngine.get(editwin)
        self.is_replace = is_replace

        self.top = editwin.top
        self.pack_after = pack_after

        self.widgets_built = False
        self.shown = False

        self.find_var = Tkinter.StringVar(self.root)

        # The text widget's selection isn't shown when it doesn't have the
        # focus. The "findsel" tag looks like the selection, and will be used
        # while the search bar is visible. When the search bar is hidden, the
        # original selection is updated as required.
        #
        # This also allows saving the original selection. If the search bar is
        # hidden with no selected search hit, the original selection is
        # restored.
        self.text.tag_configure("findsel",
            background=self.text.tag_cget("sel","background"),
            foreground=self.text.tag_cget("sel","foreground"))

        self._hide()

    def _show(self):
        if not self.widgets_built:
            self._build_widgets()
            
        if not self.shown:
            orig_geom = self.top.wm_geometry()
            self.bar_frame.pack(side=BOTTOM, fill=X, expand=0, pady=1,
                                after=self.pack_after)
            # Reset the window's size only if it is in 'normal' state.
            # On Windows, if this is done when the window is maximized
            # ('zoomed' state), then the window will not return to its
            # original size when it is unmaximized.
            if self.top.wm_state() == 'normal':
                self.top.wm_geometry(orig_geom)
                # Ensure that the insertion point is still visible
                self.top.update()
                self.text.see("insert")

            self.window_engine.show_find_marks()
            self.shown = True # must be _before_ reset_selection()!
            # Add the "findsel" tag, which looks like the selection
            self._reset_selection()            

        self._is_incremental = self.is_incremental()

    def _hide(self):
        if self.widgets_built and self.shown:
            self.bar_frame.pack_forget()
            self.window_engine.reset()
            self.window_engine.hide_find_marks()

            sel = self._get_selection()
            self.shown = False # must be _after_ get_selection()!
            if sel:
                self._set_selection(sel[0], sel[1])
                self.text.mark_set("insert", sel[0])
            else:
                self._reset_selection()
            self.text.see("insert")

        self.text.tag_remove("findsel","1.0","end")
        self._is_incremental = None

    def is_incremental(self):
        if self._is_incremental is None:
            return idleConf.GetOption("extensions", "SearchBar",
                                      "is_incremental", type="bool",
                                      default=False)
        else:
            return self._is_incremental

    def _incremental_callback(self, *args):
        if self.shown and self.is_incremental():
            if self.find_var.get():
                self._safe_search(start=self.text.index("insert"))
            else:
                self.window_engine.reset()
                self._clear_selection()
                self.text.see("insert")

    def _build_widgets(self):
        if self.widgets_built:
            return

        def _make_entry(parent, label_text, var):
            label = Tkinter.Label(parent, text=label_text)
            label.pack(side=LEFT, fill=NONE, expand=0)
            entry = Tkinter.Entry(parent, textvariable=var, exportselection=0,
                              width=30, border=1)
            entry.pack(side=LEFT, fill=NONE, expand=0)
            entry.bind("<Escape>", self.hide_findbar_event)
            return entry

        def _make_checkbutton(parent, label_text, var):
            btn = Tkinter.Checkbutton(parent, anchor="w",
                                      text=label_text, variable=var)
            btn.pack(side=LEFT, fill=NONE, expand=0)
            btn.bind("<Escape>", self.hide_findbar_event)
            return btn

        def _make_button(parent, label_text, command):
            btn = Tkinter.Button(parent, text=label_text, command=command)
            btn.pack(side=LEFT, fill=NONE, expand=0)
            btn.bind("<Escape>", self.hide_findbar_event)
            return btn

        entries = []

        # Frame for the entire bar
        self.bar_frame = Tkinter.Frame(self.top, border=1, relief="flat")

        # Frame for the 'Find:' / 'Replace:' entry + search options
        self.find_frame = Tkinter.Frame(self.bar_frame, border=0)

        # 'Find:' / 'Replace:' entry
        if not self.is_replace: tmp = "Find:"
        else: tmp = "Replace:"
        self.find_ent = _make_entry(self.find_frame,
                                    tmp, self.find_var)
        entries.append(self.find_ent)

        callback = self.find_ent._register(self._incremental_callback)
        self.find_ent.tk.call("trace", "variable", self.find_var, "w",
                              callback)

        # Regular expression checkbutton
        reg_btn = _make_checkbutton(self.find_frame,
                                    "Reg-Exp", self.engine.revar)
        if self.engine.isre():
            reg_btn.select()

        # Match case checkbutton
        case_btn = _make_checkbutton(self.find_frame,
                                     "Match case", self.engine.casevar)
        if self.engine.iscase():
            case_btn.select()

        # Whole word checkbutton
        word_btn = _make_checkbutton(self.find_frame,
                                     "Whole word", self.engine.wordvar)
        if self.engine.isword():
            word_btn.select()

        # Wrap checkbutton
        wrap_btn = _make_checkbutton(self.find_frame,
                                     "Wrap around", self.engine.wrapvar)
        if self.engine.iswrap():
            wrap_btn.select()

        # Direction checkbutton
        direction_txt_var = Tkinter.StringVar(self.root)
        def _update_direction_button():
            if self.engine.isback():
                direction_txt_var.set("Up")
            else:
                direction_txt_var.set("Down")
        direction_btn = Tkinter.Checkbutton(self.find_frame,
                                            textvariable=direction_txt_var,
                                            variable=self.engine.backvar,
                                            command=_update_direction_button,
                                            indicatoron=0,
                                            width=5)
        direction_btn.config(selectcolor=direction_btn.cget("bg"))
        direction_btn.pack(side=RIGHT, fill=NONE, expand=0)
        Tkinter.Label(self.find_frame, text="Direction:").pack(side=RIGHT,
                                                               fill=NONE,
                                                               expand=0)
        if self.engine.isback():
            direction_btn.select()
        else:
            direction_btn.deselect()
        _update_direction_button()
        direction_btn.bind("<Escape>",self.hide_findbar_event)

        self.find_frame.pack(side=TOP, fill=X, expand=0)

        if self.is_replace:
            # Frame for the 'With:' entry + replace options
            self.replace_frame = Tkinter.Frame(self.bar_frame, border=0)

            self.replace_with_var = Tkinter.StringVar(self.root)
            self.replace_ent = _make_entry(self.replace_frame,"With:",
                                           self.replace_with_var)
            entries.append(self.replace_ent)

            _make_button(self.replace_frame, "Find",
                         self._search)
            _make_button(self.replace_frame, "Replace",
                         self._replace_event)
            _make_button(self.replace_frame, "Replace All",
                         self._replace_all_event)

            self.replace_frame.pack(side=TOP, fill=X, expand=0)

        self.widgets_built = True

        if not self.is_replace:
            # Key bindings for the 'Find:' Entry widget
            self.find_ent.bind("<Return>", self._safe_search)
        else:
            # Key bindings for the 'Replace:' Entry widget
            def _find_entry_return_event(event):
                self.replace_ent.focus()
                self.replace_ent.selection_range(0,"end")
                return "break"
            self.find_ent.bind("<Return>", _find_entry_return_event)
            
            # Key bindings for the 'With:' Entry widget
            self.replace_ent.bind("<Return>", self._replace_event)
            self.replace_ent.bind("<Shift-Return>", self._safe_search)


        def _make_toggle_event(button):
            def event(event, button=button):
                button.invoke()
                return "break"
            return event

        self.entries = []
        for i in xrange(len(entries)):
            entry = entries[i]
            entry.bind("<Control-Key-f>", self._safe_search)
            entry.bind("<Control-Key-g>", self._safe_search)
            entry.bind("<Control-Key-R>", _make_toggle_event(reg_btn))
            entry.bind("<Control-Key-C>", _make_toggle_event(case_btn))
            entry.bind("<Control-Key-W>", _make_toggle_event(wrap_btn))
            entry.bind("<Control-Key-D>", _make_toggle_event(direction_btn))

            expander = EntryExpander(entry, self.text)
            expander.bind("<Alt-Key-slash>")

            self.entries.append((entry, expander))

    # end of _build_widgets

    def _destroy_widgets(self):
        if self.widgets_built:
            self.bar_frame.destroy()

    def show_findbar_event(self, event):
        # Get the current selection
        sel = self._get_selection()
        if sel:
            # Put the current selection in the "Find:" entry
            self.find_var.set(self.text.get(sel[0],sel[1]))

        # Now show the FindBar in all it's glory!
        self._show()

        # Select all of the text in the "Find:"/"Replace:" entry
        self.find_ent.selection_range(0,"end")

        # Hide the findbar if the focus is lost
        self.bar_frame.bind("<FocusOut>", self.hide_findbar_event)

        # Focus traversal (Tab or Shift-Tab) shouldn't return focus to
        # the text widget
        self.prev_text_takefocus_value = self.text.cget("takefocus")
        self.text.config(takefocus=0)

        # Set the focus to the "Find:"/"Replace:" entry
        self.find_ent.focus()
        return "break"

    def hide_findbar_event(self, event=None):
        self._hide()
        self.text.config(takefocus=self.prev_text_takefocus_value)
        self.text.focus()
        return "break"

    def search_again_event(self, event):
        if self.engine.getpat():
            return self._search(event)
        else:
            return self.show_findbar_event(event)

    def search_selection_event(self, event):
        # Get the current selection
        sel = self._get_selection()
        if not sel:
            # No selection - beep and leave
            self.text.bell()
            return "break"

        # Set the window's search engine's pattern to the current selection 
        self.find_var.set(self.text.get(sel[0],sel[1]))

        return self._search(event)

    def _search_text(self, start, is_safe):
        regexp = self._set_regexp()
        if not regexp:
            return None

        direction = not self.engine.isback()
        wrap = self.engine.iswrap()
        sel = self._get_selection()

        if start is None:
            if sel:
                _start = start = sel[0]
                
                selected_text = self.text.get(sel[0],sel[1])
                if direction and regexp.match(selected_text):
                    _start += "+1c"
            else:
                _start = start = self.text.index("insert")
        else:
            _start = start
        res = self.window_engine.findnext(regexp,
                                          _start, direction, wrap, is_safe)

        # ring the bell if the selection was found again
        if sel and start == sel[0] and res == sel:
            self.text.bell()

        return res

    def _search(self, event=None, start=None, is_safe=False):
        res = self._search_text(start, is_safe)
        if res:
            first, last = res
            self._set_selection(first, last)
            self.text.see(first)
            if not self.shown:
                self.text.mark_set("insert", first)
        else:
            self._clear_selection()
            self.text.bell()
        return "break"

    def _safe_search(self, event=None, start=None):
        return self._search(event=event, start=start, is_safe=True)

    def _replace_event(self, event=None):
        regexp = self._set_regexp()
        if not regexp:
            return "break"

        # Replace if appropriate
        sel = self._get_selection()
        if sel and regexp.match(self.text.get(sel[0], sel[1])):
            replace_with = self.replace_with_var.get()
            if Tkinter.tkinter.TK_VERSION >= '8.5':
                # Requires at least Tk 8.5!
                # This is better since the undo mechanism counts the
                # replacement as one action
                self.text.replace(sel[0],
                                  sel[1],
                                  replace_with)
            else: # TK_VERSION < 8.5 - no replace method
                if sel[0] != sel[1]:
                    self.text.delete(sel[0], sel[1])
                if replace_with:
                    self.text.insert(sel[0], replace_with)
            self.text.mark_set("insert", sel[0] + '+%dc' % len(replace_with))

        # Now search for the next appearance
        return self._search(event, is_safe=False)

    def _replace_all_event(self, event=None):
        regexp = self._set_regexp()
        if not regexp:
            return "break"

        replace_with = self.replace_with_var.get()
        n_replaced = self.window_engine.replace_all(regexp, replace_with)
        if n_replaced == 0:
            self.text.bell()
        return "break"

    def _set_regexp(self):
        search_expression = self.find_var.get()
        # If the search expression is empty, bail out.
        # (otherwise SearchEngine pops up an annoying message box)
        if not search_expression:
            return None

        self.engine.patvar.set(search_expression)
        regexp = self.engine.getprog()
        return regexp


    ### Selection related methods    
    def _clear_selection(self):
        tagname = self.shown and "findsel" or "sel"
        self.text.tag_remove(tagname, "1.0", "end")

    def _set_selection(self, start, end):
        self._clear_selection()
        tagname = self.shown and "findsel" or "sel"
        self.text.tag_add(tagname, start, end)

    def _get_selection(self):
        tagname = self.shown and "findsel" or "sel"
        return self.text.tag_nextrange(tagname, '1.0', 'end')

    def _reset_selection(self):
        if self.shown:
            sel = self.text.tag_nextrange("sel", '1.0', 'end')
            if sel:
                self._set_selection(sel[0], sel[1])
            else:
                self._clear_selection()


class EntryExpander(object):
    """Expand words in an entry, taking possible words from a text widget."""
    def __init__(self, entry, text):
        self.text = text
        self.entry = entry
        self.reset()

        self.entry.bind('<Map>', self.reset)

    def reset(self, event=None):
        self._state = None

    def bind(self, event_string):
        self.entry.bind(event_string, self._expand_word_event)

    def _expand_word_event(self, event=None):
        curinsert = self.entry.index("insert")
        curline = self.entry.get()
        if not self._state:
            words = self._get_expand_words()
            index = 0
        else:
            words, index, insert, line = self._state
            if insert != curinsert or line != curline:
                words = self._get_expand_words()
                index = 0
        if not words:
            self.text.bell()
            return "break"

        curword = self._get_curr_word()
        newword = words[index]
        index = (index + 1) % len(words)
        if index == 0:
            self.text.bell() # Warn the user that we cycled around

        idx = int(self.entry.index("insert"))
        self.entry.delete(str(idx - len(curword)), str(idx))       
        self.entry.insert("insert", newword)

        curinsert = self.entry.index("insert")
        curline = self.entry.get()        
        self._state = words, index, curinsert, curline
        return "break"
        
    def _get_expand_words(self):
        curword = self._get_curr_word()
        if not curword:
            return []

        regexp = re.compile(r"\b" + curword + r"\w+\b")
        # Start at 'insert wordend' so current word is first
        beforewords = regexp.findall(self.text.get("1.0", "insert wordend"))
        beforewords.reverse()
        afterwords = regexp.findall(self.text.get("insert wordend", "end"))
        # Interleave the lists of words
        # (This is the next best thing to sorting by distance)
        allwords = []
        for a,b in zip(beforewords, afterwords):
            allwords += [a,b]
        minlen = len(allwords)/2
        allwords += beforewords[minlen:] + afterwords[minlen:]

        words_list = []
        words_dict = {}
        for w in allwords:
            if w not in words_dict:
                words_dict[w] = w
                words_list.append(w)
        words_list.append(curword)
        return words_list

    _wordchars = string.ascii_letters + string.digits + "_"
    def _get_curr_word(self):
        line = self.entry.get()
        i = j = self.entry.index("insert")
        while i > 0 and line[i-1] in self._wordchars:
            i = i-1
        return line[i:j]
    
