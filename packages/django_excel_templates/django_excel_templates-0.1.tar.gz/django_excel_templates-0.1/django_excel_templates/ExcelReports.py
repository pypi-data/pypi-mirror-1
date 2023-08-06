import decimal, sys, traceback, StringIO
import datetime as dt
from datetime import datetime
import xlwt as xl
import helpers
from Deco import accepts, returns
from decimal import Decimal
from color_converter import *
from django.utils import encoding

REPORT_VERT,REPORT_HORZ =  range(2)
ITEM_DATE, ITEM_TIME, ITEM_DATETIME, ITEM_INT, ITEM_FLOAT, ITEM_DECIMAL, ITEM_UNICODE, ITEM_BOOL, ITEM_HEADER = range(9)
STYLE_FACTORY = {}
FONT_FACTORY = {}

class ReportStyle(object):
    
    orientation = REPORT_VERT
    
    def set_orientation(self,orientation): self.orientation = orientation
    
    def get_orientation(self): return self.orientation
        

class CellFormatter(object):
    """
    FLAGS
    =====

    norepeat  : Do not repeat if previous cell value is the same
    spreadall : take related cross-query and populate accross
    
    """
    
    def __init__(self,**kw):
        self.cellformats = {}
        if kw.has_key("norepeat"):
            fields = helpers.get_items(kw["norepeat"])
            self.cellformats['norepeat'] = fields
        if kw.has_key("spreadall"):
            fields = helpers.get_items(kw["spreadall"])
            self.cellformats['spreadall'] = fields
    
    def getCellFormats(self):
        return self.cellformats


class Item(object):
    """
    abstract Item bridges the gap between different singular data pieces and a generic type
    """
    __val = None
    __type = None
    __percision = 0
    
    def __init__(self, key, val, res, header=False):
        if header == True:
            self.__val = unicode(key)
        else:
            self.__val = val
        
        try:
            obtype = type(res.__getattribute__(key))
        except:
            obtype = unicode
        
        if header == True:
            self.__type = ITEM_HEADER
        elif obtype == unicode:
            self.__type = ITEM_UNICODE
        elif obtype  == int:
            self.__type = ITEM_INT
        elif obtype == bool:
            self.__type = ITEM_BOOL
        elif obtype == float:
            self.set_percision(0 - int(Decimal(str(val)).as_tuple()[2]) )
            self.__type = ITEM_FLOAT
        elif obtype == decimal.Decimal:
            self.set_percision( 0 - int(val.as_tuple()[2]) )
            self.__type = ITEM_DECIMAL
        elif obtype == dt.datetime:
            self.__type = ITEM_DATETIME
        elif obtype == dt.date:
            self.__type = ITEM_DATE
        elif obtype == dt.time:
            self.__type = ITEM_TIME
        
    def set_percision(self,num):
        self.__percision = num
  
    def get_percision(self):
        return self.__percision 

    def get_type(self):
        return self.__type
        
    def get_value(self):
        if self.__type == ITEM_INT:
            return int(self.__val)
        elif self.__type == ITEM_FLOAT or self.__type == ITEM_DECIMAL:
            return float(self.__val)
        elif self.__type == ITEM_DATE:
            return dt.datetime.combine(self.__val,dt.time(0,0,0))
        elif self.__type == ITEM_DATETIME or self.__type == ITEM_TIME:
            return self.__val
        else:
            #return unicode(self.__val)
            return encoding.smart_unicode(self.__val)
    
    def get_length(self):
        return len( str(self.__val) )
        
        
class BaseStyle(object):
    """
    dictionary of common style properties
    """
    __style = {}
    __pattern = []
    __alignment = []
    __border = []
    __font = []
    
    def __init__(self,**kwargs):
        
        """
        Keyword arguments:
        
        pattern_color = 6 character hexidecimal color (background color of cell) *Must be set with pattern_border
        pattern_border = 0 or 1 (Solid: 1, None: 0) *Must be set with pattern_color
        
        border_style = int (size of border in points) *Must be set with border_color
        border_color = 6 character hexidecimal color *Must be set with border_style
        
        alignment settings:
        
        dire: int *see below
        horz: int *see below
        inde: int *see below
        merg: int *see below
        orie: int *see below
        rota: int *see below
        shri: int *see below
        vert: int *see below
        wrap: int *see below
        
        font_color = 6 character hexidecimal color
        bold = True/False (font property)
        italic = True/False (font property)
        shadow = True/False (font property)
        outline = True/False (font property)
        struck_out = True/False (font property)
        underline = True/False (font property)
        height = int (200 = 10pt, 160 = 8pt)
        
        **************
        
        BORDER STYLES:
        THIN = 1
        MEDIUM = 2
        DASHED = 3
        DOTTED = 4
        THICK = 5
        DOUBLE = 6
        HAIR = 7
        MEDIUM_DASHED = 8
        THIN_DASH_DOTTED = 9
        MEDIUM_DASH_DOTTED = 10
        THIN_DASH_DOT_DOTTED = 11
        MEDIUM_DASH_DOT_DOTTED = 12
        SLANTED_MEDIUM_DASH_DOTTED = 13
        
        ***************
        *ALIGNMENT SETTINGS:
        
        "dire":
        DIRECTION_GENERAL = 0
        DIRECTION_LR = 1
        DIRECTION_RL = 2
        
        "horz":
        HORZ_GENERAL = 0
        HORZ_LEFT = 1
        HORZ_CENTER = 2
        HORZ_RIGHT = 3
        HORZ_FILLED = 4
        HORZ_JUSTIFIED = 5
        HORZ_CENTER_ACROSS_SEL = 6
        HORZ_DISTRIBUTED = 7
        
        "inde": ?
        "merg": ?
        
        "orie":
        ORIENTATION_NOT_ROTATED = 0
        ORIENTATION_STACKED = 1
        ORIENTATION_90_CC = 2
        ORIENTATION_90_CW = 3
        
        "rota":
        ROTATION_0_ANGLE = 0
        ROTATION_STACKED = 255
        
        "shri":
        NOT_SHRINK_TO_FIT = 0
        SHRINK_TO_FIT = 1
        
        "vert":
        VERT_TOP = 0
        VERT_CENTER = 1
        VERT_BOTTOM = 2
        VERT_JUSTIFIED = 3
        VERT_DISIRIBUTED = 4
        
        "wrap":
        NOT_WRAP_AT_RIGHT = 0
        WRAP_AT_RIGHT = 1
        
        """
        if kwargs.has_key('pattern_color') and kwargs.has_key('pattern'):
            self.set_pattern(pattern=kwargs['pattern'],pattern_color=kwargs['pattern_color'])        
        if kwargs.has_key('border_style') and kwargs.has_key('border_color'):
            self.set_border(border_style=kwargs['border_style'],border_color=kwargs['border_color'])
            
        dire=0
        horz=0
        inde=0
        merg=0
        orie=0
        rota=0
        shri=0
        vert=2
        wrap=0
        
        if kwargs.has_key('dire'):
            dire = kwargs['dire']
        if kwargs.has_key('horz'):
            horz = kwargs['horz']
        if kwargs.has_key('inde'):
            inde = kwargs['inde']
        if kwargs.has_key('merg'):
            merg = kwargs['merg']
        if kwargs.has_key('orie'):
            orie = kwargs['orie']
        if kwargs.has_key('rota'):
            rota = kwargs['rota']
        if kwargs.has_key('shri'):
            shri = kwargs['shri']
        if kwargs.has_key('vert'):
            vert = kwargs['vert']
        if kwargs.has_key('wrap'):
            wrap = kwargs['wrap']
        self.set_alignment(dire,horz,inde,merg,orie,rota,shri,vert,wrap)
        
        font_color = '000000'
        height = 200
        bold = False
        italic = False
        shadow = False
        outline = False
        struck_out = False
        underline = False
        
        if kwargs.has_key('font_color'):
            font_color=kwargs['font_color']
        if kwargs.has_key('bold'):
            bold=kwargs['bold']      
        if kwargs.has_key('italic'):
            italic=kwargs['italic']
        if kwargs.has_key('shadow'):
            shadow=kwargs['shadow']
        if kwargs.has_key('outline'):
            outline=kwargs['outline']       
        if kwargs.has_key('struck_out'):
            struck_out=kwargs['struck_out']
        if kwargs.has_key('underline'):
            underline=kwargs['underline']
        if kwargs.has_key('height'):
            height=kwargs['height']
        self.set_font(font_color=font_color,bold=bold,italic=italic,outline=outline,struck_out=struck_out,underline=underline,height=height)
            
    def set_pattern(self,pattern_color=False,pattern=False):
        self.__pattern = []
        if pattern_color:
            _pattern_back_colour = ('_pattern_back_colour',get_closest_rgb_match(self.get_color_dict(), pattern_color))
            _pattern_fore_colour = ('_pattern_fore_colour',get_closest_rgb_match(self.get_color_dict(), pattern_color))
            self.__pattern.extend((_pattern_back_colour,_pattern_fore_colour))
        if pattern:
            pattern_style = ('pattern',pattern)
            self.__pattern.append(pattern_style)
            
    def set_alignment(self,dire=0,horz=0,inde=0,merg=0,orie=0,rota=0,shri=0,vert=2,wrap=0):
        align_dire = ('dire',dire)
        align_horz = ('horz',horz)
        align_inde = ('inde',inde)
        align_merg = ('merg',merg)
        align_orie = ('orie',orie)
        align_rota = ('rota',rota)
        align_shri = ('shri',shri)
        align_vert = ('vert',vert)
        align_wrap = ('wrap',wrap)
        self.__alignment.extend((align_dire,align_horz,align_inde,align_merg,align_orie,align_rota,align_shri,align_vert,align_wrap))
     
    def set_border(self,border_color=False,border_style=False):
        self.__border = []
        size = 0
        color = 'FFFFFF'
        if border_style:
            size = border_style
        if border_color:
            color = get_closest_rgb_match(self.get_color_dict(), border_color)
        border_bottom = ('bottom',size)
        border_bottom_colour = ('bottom_colour',color)
        border_left = ('left',size)
        border_left_colour = ('left_colour',color)
        border_right = ('right',size)
        border_right_colour = ('right_colour',color)
        border_top = ('top',size)
        border_top_colour = ('top_colour',color)
        self.__border.extend((border_bottom,border_bottom_colour,border_left,border_left_colour,border_right,border_right_colour,border_top,border_top_colour))

    def set_font(self,font_color=False,bold=False,italic=False,outline=False,shadow=False,struck_out=False,underline=False,height=False):
        self.__font = []
        if font_color:
            font_colour = ('colour_index',get_closest_rgb_match(self.get_color_dict(), font_color))
            self.__font.append(font_colour)
        if bold:
            font_bold = ('bold',bold)
            self.__font.append(font_bold)
        if italic:
            font_italic = ('italic',italic)
            self.__font.append(font_italic)
        if outline:
            font_outline = ('outline',outline)
            self.__font.append(font_outline)
        if shadow:
            font_shadow = ('shadow',shadow)
            self.__font.append(font_shadow)
        if struck_out:
            font_struck_out = ('struck_out',struck_out)
            self.__font.append(font_struck_out)
        if underline:
            font_underline = ('underline',underline)
            self.__font.append(font_underline)
        if height:
            font_height = ('height',height)
            self.__font.append(font_height)
    
    def get_style(self):
        return self.__style
    
    def get_pattern(self):
        return self.__pattern
    
    def get_alignment(self):
        return self.__alignment
    
    def get_border(self):
        return self.__border
    
    def get_font(self):
        return self.__font
    
    def get_style_dict(self):
        self.__style = {}
        self.__style['pattern'] = self.__pattern
        self.__style['alignment'] = self.__alignment
        self.__style['border'] = self.__border
        self.__style['font'] = self.__font
        return self.__style

    def get_color_dict(self):
        abstract()
   
class ExcelStyle(BaseStyle):
    """
    Takes BaseStyle object, uses Excel color dictionary, and will create XFStyle object for Excel.
    """
    
    def get_color_dict(self):
        return get_excel_color_dict() 
        
    def get_excel_font(self,values):
        f = FONT_FACTORY.get(str(values), None)
        if f is None:
            font_key = values
            f = xl.Font()
            for attr, value in values:
                f.__setattr__(attr, value)
            FONT_FACTORY[str(values)] = f
        return f

    def get_excel_style(self):
        style = self.get_style_dict()
        s = STYLE_FACTORY.get(str(style), None)
        if s is None:
            s = xl.XFStyle()
            style_key = tuple(style.items())
            for key, values in style.items():
                if key == "pattern":
                    p = xl.Pattern()
                    for attr, value in values:
                        if attr == '_pattern_back_colour':
                            p.pattern_back_colour = value
                        elif attr == '_pattern_fore_colour':
                            p.pattern_fore_colour = value
                        else:
                            p.__setattr__(attr,value)
                    s.pattern = p
                elif key == "alignment":
                    a = xl.Alignment()
                    for attr, value in values:
                        a.__setattr__(attr,value)
                    s.alignment = a
                elif key == "border":
                    b = xl.Borders()
                    for attr, value in values:
                        b.__setattr__(attr,value)
                    s.borders = b
                elif key == "font":
                    f = self.get_excel_font(values)
                    s.font = f
            STYLE_FACTORY[str(style)] = s
        return s
    

class GridException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


class Grid(object):
    """
    always square, easily add items.
    
    'None' is a valid place holder for no data
    """
    
    
    def __init__(self):
        self.grid = []
        
        
    def get_max_y(self):
        i = 0
        for x in self.grid:
            if len(x) > i:
                i = len(x)
        return i
    
    def square_grid(self,y):
        max_y = self.get_max_y()
        if max_y < y:
            max_y = y + 1
        i = 0
        while i < len(self.grid):
            if len(self.grid[i]) < max_y:
                diff = max_y - len(self.grid[i])
                while diff > 0:
                    self.grid[i].append(None)
                    diff -= 1
            i += 1
    
    @accepts(object,int,int,Item)
    def add(self,x,y,val):
        
        xlen = len(self.grid)
        # make row(s), if needed
        if x >= xlen:
            if x == xlen:
                self.grid.append([])
                self.grid[xlen].append(None)
            else:
                i = xlen
                while x >= i:
                    self.grid.append([])
                    self.grid[i].append(None)
                    i += 1
    
        self.square_grid(y)
    
        ylen = len(self.grid[x])
        # make column(s) if needed
        if y >= ylen:
            if y == ylen:
                self.grid[x].append(None)
            else:
                i = x
                while y <= i:
                    self.grid[i].append(None)
                    i += 1
    
        if self.grid[x][y] == None:
            self.grid[x][y] = val
        else:
            raise GridException('Attempting to populate already populated cell at (%s,%s).' % (x,y))
    
    def getGrid(self):
        return self.grid


class BaseDump(object):
    
    def __init__(self):
        super(BaseDump, self).__init__()
        self.filters = {}
    
    def addFilter(self,**kwargs):
        """
        Keyword Arguments:
        include: instance fields to include, accepts single field, or comma seperated fields.
        formatter.addFilter(include='DateField,FloatField,SlugField')
        exclude: instance fields to exclude, accepts single field, or comma seperated fields.
        formatter.addFilter(exclude='DateField')
        order: order the instance fields, accepts single field, or comma seperated fields.
        formatter.addFilter(order='FloatField,DateField,SlugField)
        
        """
        self.includes = []
        self.excludes = []
        self.order = []
        self.filter = {}
        
        if kwargs.has_key('include'):
            for i in helpers.get_items(kwargs['include']):
                self.includes.append(i)
                self.filter['include'] = self.includes
        if kwargs.has_key('exclude'):
            for i in helpers.get_items(kwargs['exclude']):
                self.excludes.append(i)
                self.filter['exclude'] = self.excludes
        if kwargs.has_key('order'):
            for i in helpers.get_items(kwargs['order']):
                self.order.append(i)
                self.filter['order'] = self.order
                
        self.filters[self.current_sheet] = self.filter
        
    def getFilter(self):
            
        return self.filters
    
    def django_dump_obj(self,res,headers=False):
        out = []
        keys = None
        # check for foreignkey/manytomany
        fkrelations = helpers.get_relation_list(res,FK=True)
        m2mrelations = helpers.get_relation_list(res)
        if fkrelations:
            res.__dict__.update(fkrelations)
        if m2mrelations:
            res.__dict__.update(m2mrelations)
        
        iterdict = res.__dict__
        keys = iterdict.keys()
        included = None
        excluded = None
        ordered = None
        #filters order/include/exclude
        if self.getFilter()[self.current_sheet] != {}:
            if self.getFilter()[self.current_sheet].has_key('include'):
                included = self.getFilter()[self.current_sheet]['include']
            if self.getFilter()[self.current_sheet].has_key('exclude'):
                excluded = self.getFilter()[self.current_sheet]['exclude']
            if self.getFilter()[self.current_sheet].has_key('order'):
                keys = self.getFilter()[self.current_sheet]['order']
        i = 0
        
        while i < len(keys):
            if included:
                if keys[i] not in included:
                    i += 1
                    continue
            if excluded:
                if keys[i] in excluded:
                    i += 1
                    continue
            if headers:
                self.grids[self.current_sheet].add(self.current_x,self.current_y,Item(keys[i],iterdict[keys[i]],res,header=True))
                self.change_column_position()
                i += 1
                continue
            self.grids[self.current_sheet].add(self.current_x,self.current_y,Item(keys[i],iterdict[keys[i]],res))
            self.change_column_position()
            i += 1
        self.change_row_position()
    
    def change_column_position(self):
        if self.report_style.get_orientation() == REPORT_VERT:
            self.current_y += 1
        else:
            self.current_x += 1
    
    def change_row_position(self):
        if self.report_style.get_orientation() == REPORT_VERT:
            self.current_x += 1
            self.current_y = 0
        else:
            self.current_y += 1
            self.current_x = 0

class BaseReport(BaseDump):
    """
        Abstract BaseReport Class used by various reports
        
    """
    
    def __init__(self):
        super(BaseReport, self).__init__()
        self.grids = {}
        self.current_sheet = None
        self.current_x = self.current_y = 0
        self.report_style = ReportStyle()
        self.sheetcount = 0
        self.formatter = {}
    
    def add_one_instance(self,inst,orientation,addheader=False):
        """
        Deprecated. Votovox is using this.
        """
        self.addQuerySet(inst,orientation,addheader)
            
    def addQuerySet(self,inst,orientation,addheader=False):
        self.grids[self.current_sheet] = Grid()
        self.current_x = self.current_y = 0
        self.report_style.set_orientation(orientation)
        headersadded = False
        for i in inst:
            if addheader and not headersadded:
                self.django_dump_obj(i,headers=True)
                headersadded = True
            self.django_dump_obj(i)

    @accepts(object,object)
    def addFormatter(self,formatter):
        self.formatter[self.current_sheet] = formatter
    
    def getFormatter(self):
        return self.formatter
        

    formatters = {}

    def __get_format(self,key):
        if self.formatters.has_key(key):
            return self.formatters[key]
        elif self.formatters.has_key("DEFAULT"):
            return self.formatters["DEFAULT"]
        return u''
    
    @accepts(object,Item)
    def get_format(self,item):
        format = self.__get_format(item.get_type())
        if callable(format):
            return format(item)
        return format

    def addSheet(self,name=None):
        self.sheetcount += 1
        if name == None:
            name = "Untitled Sheet #%s" % self.sheetcount
        self.current_sheet = name
        self.filters[self.current_sheet] = {}
        self.formatter[self.current_sheet] = {}
        
class ExcelReport(BaseReport):
    """ MS Excel Style Reports """    
    workbook = None
    tempf = None
    CHAR_WIDTH = 275
    
    def __init__(self):
        self.workbook = xl.Workbook()
        self.workbook._Workbook__use_cell_values = 0
        self.cellformatters = {}
        super(ExcelReport, self).__init__()
     
    def __del__(self):
        if self.tempf and not self.tempf.closed:
            self.tempf.close()
    
    def addCellFormatter(self,CellFormatter):
        self.cellformatters[self.current_sheet] = CellFormatter
        
    def getCellFormatter(self):
        return self.cellformatters
    
    def nextsheet(self,name=None):
        """
        Deprecated. Votovox is using this.
        """
        self.addSheet(name)
    
    def output(self):
        """
        Deprecated. Votovox is using this.
        """
        self.writeReport(self)
    
    def writeReport(self):
        if not self.tempf:
            self.tempf = StringIO.StringIO()
            
        for k, v in self.grids.iteritems():
            self.current_x = 0
            self.current_y = 0
            ws = self.workbook.add_sheet(k)
            grid = v.getGrid()
            for col in grid:
                header_value = ''
                for item in col:
                    if item.get_type() == ITEM_HEADER:
                        header_value = item.get_value()
                    if self.getFormatter()[k] != {}:
                        if item.get_type() == ITEM_HEADER and self.getFormatter()[k].header_style is not None:
                            self.style = self.getFormatter()[k].getHeaderStyle()
                        elif self.getFormatter()[k].col_styles != {} and self.getFormatter()[k].getColumnStyle().has_key(header_value):
                            self.style = self.getFormatter()[k].getColumnStyle(header_value)
                        elif self.getFormatter()[k].alternate_color_style is not None and not helpers.isodd(self.current_x):
                            self.style = self.getFormatter()[k].getAlternateColorStyle()
                        elif self.getFormatter()[k].body_style is not None:
                            self.style = self.getFormatter()[k].getBodyStyle()
                        else:
                            self.style = ExcelStyle().get_excel_style()
                        if self.getFormatter()[k].getWidth() != {}:
                            if self.getFormatter()[k].getWidth().has_key(header_value):
                                setwidth = self.getFormatter()[k].getWidth()[header_value]
                                self.__adjustwidth(item,setwidth)
                            else:
                                self.__adjustwidth(item)
                    else:
                        self.__adjustwidth(item)
                        self.style = ExcelStyle().get_excel_style()
                    if self.get_format(item) != self.formatters['DEFAULT']:
                        self.style.num_format_str = self.get_format(item)
                    ws.write(
                        self.current_x,
                        self.current_y,
                        item.get_value(),
                        self.style
                        )
                    self.change_column_position()
                if self.getFormatter()[k] != {}:
                    if self.getFormatter()[k].getFormula().has_key(header_value):
                        excel_formula = '%s(%s%s:%s%s)' % (self.formatter.getFormula()[k][header_value],
                                                           helpers.convert_to_letter(self.current_y),'2',
                                                           helpers.convert_to_letter(self.current_y),
                                                           self.current_x - 1)
                        self.style = ExcelStyle().get_excel_style()
                        ws.write(self.current_x,self.current_y,xl.Formula(excel_formula),self.style)
                self.change_row_position()
        self.workbook.save(self.tempf)
        return self.tempf.getvalue()


    def __func_for_nums(item):
        i = 0
        style = '0.'
        while i < item.get_percision():
            style += '0'
            i += 1
        return style



    formatters = {
        ITEM_DATETIME: 'M/D/YYYY h:mm:ss',
        ITEM_DATE: 'M/D/YYYY',
        ITEM_TIME: 'h:mm:ss',
        ITEM_FLOAT: __func_for_nums,
        ITEM_DECIMAL: __func_for_nums,
        ITEM_INT: '0',
        'DEFAULT': u'',
    }
    
    
    # Private internal methods
    def __cellcord(self):
        return self.current_x,self.current_y
    
    def __cursheet(self):
        return self.workbook.get_sheet(self.sheetcount-2)
    
    def __adjustwidth(self,item,setwidth=0):
        newlen =  item.get_length() * self.CHAR_WIDTH
        if self.__cursheet().col(self.current_x).width < newlen:
            if setwidth != 0:
                newlen = setwidth
            self.__cursheet().col(self.current_y).width = newlen
            


class BaseFormatter(object):
    """
        Abstract BaseFormatter Class used by various reports
        
    """
    
    def __init__(self):
        self.header_style = None
        self.alternate_color_style = None
        self.body_style = None
        self.set_widths = {}
        self.formulas = {}
        self.col_styles = {}
    
    @accepts(object,str,int)
    def setWidth(self,fields,width):
        sortedfields = helpers.get_items(fields)
        for field in sortedfields:
            self.set_widths[field] = width
    
    def getWidth(self):
        return self.set_widths
    

class ExcelFormatter(BaseFormatter):

    @accepts(object,BaseStyle)
    def addHeaderStyle(self,style):
        self.header_style = style
        
    @accepts(object,BaseStyle)
    def addAlternateColorStyle(self,style):
        self.alternate_color_style = style
    
    @accepts(object,BaseStyle)
    def addBodyStyle(self,style):
        self.body_style = style

    @accepts(object,str,str)
    def addFormula(self,fields,function):
        sortedfields = helpers.get_items(fields)
        for field in sortedfields:
            self.formulas[field] = function

    def getFormula(self):
        return self.formulas
    
    @accepts(object,str,BaseStyle)
    def addColumnStyle(self,fields,style):
        sortedfields = helpers.get_items(fields)
        for field in sortedfields:
            self.col_styles[field] = style
            
    def getColumnStyle(self,field=None):
        if field:
            return self.col_styles[field].get_excel_style()
        else:
            return self.col_styles

    def getHeaderStyle(self):
        return self.header_style.get_excel_style()
    
    def getAlternateColorStyle(self):
        return self.alternate_color_style.get_excel_style()
    
    def getBodyStyle(self):
        return self.body_style.get_excel_style()
    
def logerror(Exception, e):
    note = str(e)
    note += "\n\n"
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    for line in traceback.format_exc().splitlines():
        note += "%s\n" % line
    print note

