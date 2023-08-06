# -*- coding: utf-8 -*-

import pygame

__author__ = "Keul - lucafbb AT gmail.com"
__version__ = "0.1.0"
__description__ = "A PyGame addon for display text over surface with many dimension bounds"

LL_CUT = "cut"
LL_SPLIT = "split"
LL_OVERFLOW = "overflow"

PL_OVERFLOW = "overflow"
PL_CUT = "cut"

class KTextSurfaceWriter(object):
    """Generate a text displayed inside a given pygame.Rect.
    You can change/choose font size and color, and can fill the surface part.
    """
    
    def __init__(self, rect, font=None, color=(0,0,255,0), fillcolor=(0,0,0,0), justify_chars=0):
        self.rect = rect
        if not font:
            self.font = pygame.font.Font(None, 16)
        else:
            self.font = font
        self.fillcolor = fillcolor
        self.color = color
        self._text = "KTextSurfaceWriter - version %s" % __version__
        self._resultPage = []
        self.justify_chars = justify_chars
        self._mustClear = True
        self.line_length_criteria = LL_CUT
        self.page_length_criteria = PL_OVERFLOW

    def _setText(self, text):
        self._text = text
        self.invalidate()
    text = property(lambda self: self._text, _setText, doc="""The text to be displayed""")

    def invalidate(self):
        """Manually invalidate the text cache"""
        self._resultPage = []
        self._mustClear = True        

    @classmethod
    def wordTooLong(cls, word, font, max_length, justify_chars=0):
        """test if a single word is too long to the displayed with the given font.
        @word: the word to check
        @font: the pygame.Font to use
        @max_length: the max length of the word
        @justify_chars: an integer that add a number of spaces at the worrd total length.
        @return: True if the word will be longer
        """
        # BBB: someday this function could became part of some text (non graphical) utility?
        return font.size((" "*justify_chars)+word)[0]>max_length

    @classmethod
    def normalizeTextLength(cls, text_too_long, font, max_length, justify_chars=0, line_length_criteria=LL_CUT):
        """This function take a text too long and split it in a list of smaller text lines.
        The final text max length must be less/equals than max_length parameter, using the font passed.
        
        @return: a list of text lines.
        """
        # BBB: someday this function could became part of some text (non graphical) utility?
        words = [x for x in text_too_long.split(" ")]
        words_removed = []
        tooLong = True
        txt1 = txt2 = ""
        while tooLong:
            word = words.pop()
            if line_length_criteria.lower()==LL_CUT:
                # Simple: cut the word and go on
                while cls.wordTooLong(word, font, max_length, justify_chars=justify_chars):
                    word = word[:-1].strip()
            elif line_length_criteria.lower()==LL_SPLIT:
                # Cut the word, re-insert the remaining part as a new word and start again
                if cls.wordTooLong(word, font, max_length, justify_chars=justify_chars):
                    left_word = word
                    while cls.wordTooLong(left_word, font, max_length, justify_chars=justify_chars):
                        left_word = left_word[:-1].strip()
                    words.extend( [left_word, word[len(left_word):], ] )
                    continue
            elif line_length_criteria.lower()==LL_OVERFLOW:
                # Word too long is not changed, so draw outside the defined rect
                txt1 = " ".join(words)
                if cls.wordTooLong(word, font, max_length, justify_chars=justify_chars):
                    words_removed.reverse()
                    txt2 = (" "*justify_chars) + " ".join(words_removed)
                    if font.size(txt2)[0]<=max_length:
                        return cls.normalizeTextLength(txt1, font, max_length, justify_chars=justify_chars) + \
                               [(" "*justify_chars) + word, txt2]
                    else:
                        return cls.normalizeTextLength(txt1, font, max_length, justify_chars=justify_chars) + \
                               [(" "*justify_chars) + word] + \
                               cls.normalizeTextLength(txt2, font, max_length, justify_chars=justify_chars)
            else:
                raise ValueError("Invalid line_length_criteria value: %s" % line_length_criteria)
            words_removed.append(word)
            txt1 = " ".join(words)
            if font.size(txt1)[0]<=max_length:
                tooLong = False
        words_removed.reverse()
        txt2 = (" "*justify_chars) + " ".join(words_removed)
        if font.size(txt2)[0]<=max_length:
            return [txt1, txt2]
        else:
            return [txt1] + cls.normalizeTextLength(txt2, font, max_length, justify_chars=justify_chars)

    def _getPreparedText(self):
        """Prepare text for future rendering.
        @return: a list of all lines to be drawn
        """
        if self._resultPage:
            return self._resultPage
        rw = self.rect.width
        rh = self.rect.height
        text = self.text
        resultPage = []
        for line in text.split("\n"):
            lw, lh = self.font.size(line)
            if lw>rw:
                newtextlines = self.normalizeTextLength(line,
                                                        self.font,
                                                        rw,
                                                        justify_chars=self.justify_chars,
                                                        line_length_criteria=self.line_length_criteria)
            else:
                newtextlines = [line,]
            resultPage.extend(newtextlines)
        if self.page_length_criteria==PL_CUT:
            resultPage = self._shortDownPage(resultPage)
        self._resultPage = resultPage
        return resultPage

    def _shortDownPage(self, page, start_from_line=0):
        """If the page is too tall with the current font, this method will
        remove as many lines as needed to fith the text inside the
        constraint rect
        @page: the list of lines text
        @start_from_line: use this to not keep the page from the beginning
        @return: the page parameter without the not needed lines.
        """
        ln = len(page)
        while ln*self.font.get_height()>self.rect.height:
            page.pop()
            ln = len(page)
        return page

    def clear(self, surface, fillcolor=None):
        """Clear the subsurface with the fillcolor choosen"""
        if not fillcolor:
            fillcolor = self.fillcolor
        subs = surface.subsurface(self.rect)
        subs.fill(fillcolor)

    def draw(self, surface):
        """Draw the text to the surface."""
        if self._mustClear:
            self.clear(surface)
            self._mustClear = False
        resultPage = self._getPreparedText()
        rect = self.rect
        i = 0
        for line in resultPage:
            ren = self.font.render(line, 1, self.color, self.fillcolor)
            surface.blit(ren, (rect.left, rect.top + i*self.font.get_height()))
            i+=1


def runTests():
    """Just run the doctest"""
    import tests