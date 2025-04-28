from enum import Enum

class FontFlag(Enum):
    """
    Enum representing the font flags used by PyMuPDF.
    """
    FONT_BOLD = 65536
    FONT_ITALIC = 1
    FONT_SERIF = 4
    FONT_MONOSPACE = 8
    FONT_SYMBOL = 32
    FONT_SCRIPT = 128
    FONT_NON_ROMAN = 2048
    FONT_FIXED_WIDTH = 8
    FONT_SMALL_CAPS = 1024
    FONT_FORCE_BOLD = 131072
    FONT_FORCE_ITALIC = 2
    
    @classmethod
    def is_italic(cls, val:int):
        return val & cls.FONT_ITALIC.value  == cls.FONT_ITALIC.value or val & cls.FONT_FORCE_ITALIC.value == cls.FONT_FORCE_ITALIC.value
    
    @classmethod
    def is_bold(cls, val:int):
        return val & cls.FONT_BOLD.value == cls.FONT_BOLD.value or val & cls.FONT_FORCE_BOLD.value == cls.FONT_FORCE_BOLD.value
    

