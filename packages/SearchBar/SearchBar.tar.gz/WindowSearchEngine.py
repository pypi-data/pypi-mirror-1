import Tkinter

from configHandler import idleConf

def get(editwin):
    if not hasattr(editwin, "_window_search_engine"):
        editwin._window_search_engine = WindowSearchEngine(editwin.text)
    return editwin._window_search_engine

class WindowSearchEngine:
    def __init__(self, text):
        self.text = text

        self.hide_find_marks() # initialize 'findmark' tag        
        self.reset()

    def __del__(self):
        self.text.tag_delete("findmark")

    def show_find_marks(self):
        # Get the highlight colors for 'hit'
        # Do this here (and not in __init__) for color config changes to take
        # effect immediately
        currentTheme = idleConf.CurrentTheme()
        mark_fg = idleConf.GetHighlight(currentTheme, 'hit', fgBg='fg')
        mark_bg = idleConf.GetHighlight(currentTheme, 'hit', fgBg='bg')

        self.text.tag_configure("findmark",
                                foreground=mark_fg,
                                background=mark_bg)

    def hide_find_marks(self):
        self.text.tag_configure("findmark",
                                foreground='',
                                background='')

    def reset(self):
        self.text.tag_remove("findmark", "1.0", "end")
        self.regexp = None

    def _set_regexp(self, regexp):
        """
        1) Set the current regular expression
        2) Search for all matches in the text
        3) Mark each match with the "findmark" tag

        """
        ## XXX TODO?
        ## When searching for an extension of the previous search,
        ## i.e. regexp.startswith(self.regexp), update hits instead of starting from
        ## scratch
        self.reset()
        self.regexp = regexp

        # The search & tag algorithm has been optimized by counting the number
        # of line breaks before each hit. This allows using precise index
        # identifiers for the Text widget, instead of "1.0+<index in string>c",
        # which speeds up the setting of tags immensely.
        txt = self.text.get("1.0", "end-1c")
        prev = 0
        line = 1
        rfind = txt.rfind
        tag_add = self.text.tag_add
        for res in regexp.finditer(txt):
            start, end = res.span()
            line += txt[prev:start].count('\n')
            prev = start
            start_idx = "%d.%d" % (line,
                                   start - (rfind('\n', 0, start) + 1))
            end_idx = start_idx + '+%dc'%(end-start)
            tag_add("findmark", start_idx, end_idx)

    def findnext(self, regexp, start, direction=1, wrap=True, is_safe=False):
        """Find the next text sequence which matches the given regexp.

        The 'next' sequence is the one after the selection or the insert
        cursor, or before if the direction is up instead of down.

        The 'is_safe' argument tells whether it is safe to assume that the text
        being searched has not been changed since the previous search; if the
        text hasn't been changed then the search is almost trivial (due to
        pre-processing).
        
        """
        if regexp != self.regexp or not is_safe:
            self._set_regexp(regexp)

        # Search!
        if direction:
            next = self.text.tag_nextrange("findmark", start)
            if not next and wrap:
                next = self.text.tag_nextrange("findmark", "1.0", start)
        else:
            next = self.text.tag_prevrange("findmark", start)
            if not next and wrap:
                next = self.text.tag_prevrange("findmark", 'end', start)
    
        return next
        
    def replace_all(self, regexp, replace_with):
        n_replaced = 0
        hit = self.findnext(regexp, "1.0",
                            direction=1, wrap=False, is_safe=False)
        while hit:
            n_replaced += 1
            first, last = hit
            if Tkinter.tkinter.TK_VERSION >= '8.5':
                # Requires at least Tk 8.5!
                # This is better since the undo mechanism counts the
                # replacement as one action
                self.text.replace(first,
                                  last,
                                  replace_with)
            else: # TK_VERSION < 8.5 - no replace method
                if first != last:
                    self.text.delete(first, last)
                if replace_with:
                    self.text.insert(first, replace_with)
            hit = self.findnext(regexp, first + '+%dc' % len(replace_with),
                                direction=1, wrap=False, is_safe=True)
        return n_replaced

##def get_selection(text):
##    "Get the selection range in a text widget"
##    tmp = text.tag_nextrange("sel","1.0","end")
##    if tmp:
##        first, last = tmp
##    else:
##        first = last = text.index("insert")
##    return first, last
