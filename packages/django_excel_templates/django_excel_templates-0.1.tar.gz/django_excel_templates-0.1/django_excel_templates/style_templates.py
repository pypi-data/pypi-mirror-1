
def sample_style1():
    style = {}
    pattern = []
    alignment = []
    border = []
    font = []
    # Colors: 0- Black, 1- White, 2- Red, 3- Green, 4- Blue, 5- Yellow, 6- Magenta, 7- Cyan
    
    # Font Styles
    font_colour = ('colour_index',3)
    font_bold = ('bold',True)
    font_italic = ('italic',False)
    font_outline = ('outline',False)
    font_shadow = ('shadow',False)
    font_struck_out = ('struck_out',False)
    font_underline = ('underline',False)
    font_height = ('height',200)
    font.extend((font_colour,font_bold,font_italic,font_outline,font_shadow,font_struck_out,font_underline,font_height))
    
    # Border Styles
    border_bottom = ('bottom',2)
    border_bottom_colour = ('bottom_colour',2)
    border_left = ('left',2)
    border_left_colour = ('left_colour',4)
    border_right = ('right',2)
    border_right_colour = ('right_colour',4)
    border_top = ('top',2)
    border_top_colour = ('top_colour',2)
    border.extend((border_bottom,border_bottom_colour,border_left,border_left_colour,border_right,border_right_colour,border_top,border_top_colour))
    
    # Pattern Styles (for background)
    _pattern_back_colour = ('_pattern_back_colour',0)
    _pattern_fore_colour = ('_pattern_fore_colour',0)
    pattern_style = ('pattern',7)
    pattern.extend((_pattern_back_colour,_pattern_fore_colour,pattern_style))
    
    # Alignment Styles
    # DIRE - (0-General, 1-LeftRight, 2-RightLeft)
    # HORZ - (0-General, 1-Left, 2-Center, 3-Right, 4-Filled, 5-Justified, 6-CenterAcrossSel, 7-Distributed)
    # INDE ?
    # MERG ?
    # ORIE - (0-Not Rotated, 1-Stacked, 2-90CC, 3-90CW)
    # ROTA - (0-360 ?)
    # SHRI- (0-None, 1-Shrink To Fit)
    # VERT - (0-Top, 1-Center, 2-Bottom, 3-Justified, 4-Distributed)
    # WRAP - (0-None, 1-Wrap At Right)
    
    dire = ('dire',2)
    horz = ('horz',5)
    inde = ('inde',0)
    merg = ('merg',0)
    orie = ('orie',3)
    rota = ('rota',0)
    shri = ('shri',0)
    vert = ('vert',4)
    wrap = ('wrap',0)

    alignment.extend((dire,horz,inde,merg,orie,rota,shri,vert,wrap))
    
    style['pattern'] = pattern
    style['alignment'] = alignment
    style['border'] = border
    style['font'] = font

    return style

def sample_style2():
    style = {}
    pattern = []
    alignment = []
    border = []
    font = []
    # Colors: 0- Black, 1- White, 2- Red, 3- Green, 4- Blue, 5- Yellow, 6- Magenta, 7- Cyan
    
    # Font Styles
    font_colour = ('colour_index',3)
    font_bold = ('bold',False)
    font_italic = ('italic',True)
    font_outline = ('outline',False)
    font_shadow = ('shadow',False)
    font_struck_out = ('struck_out',False)
    font_underline = ('underline',False)
    font_height = ('height',200)
    font.extend((font_colour,font_bold,font_italic,font_outline,font_shadow,font_struck_out,font_underline,font_height))
    
    # Border Styles
    border_bottom = ('bottom',7)
    border_bottom_colour = ('bottom_colour',3)
    border_left = ('left',4)
    border_left_colour = ('left_colour',3)
    border_right = ('right',4)
    border_right_colour = ('right_colour',3)
    border_top = ('top',2)
    border_top_colour = ('top_colour',7)
    border.extend((border_bottom,border_bottom_colour,border_left,border_left_colour,border_right,border_right_colour,border_top,border_top_colour))
    
    # Pattern Styles (for background)
    _pattern_back_colour = ('_pattern_back_colour',0)
    _pattern_fore_colour = ('_pattern_fore_colour',0)
    pattern_style = ('pattern',7)
    pattern.extend((_pattern_back_colour,_pattern_fore_colour,pattern_style))

    # Alignment Styles    
    dire = ('dire',2)
    horz = ('horz',5)
    inde = ('inde',0)
    merg = ('merg',0)
    orie = ('orie',3)
    rota = ('rota',0)
    shri = ('shri',0)
    vert = ('vert',4)
    wrap = ('wrap',0)

    alignment.extend((dire,horz,inde,merg,orie,rota,shri,vert,wrap))
    
    style['pattern'] = pattern
    style['alignment'] = alignment
    style['border'] = border
    style['font'] = font

    return style
