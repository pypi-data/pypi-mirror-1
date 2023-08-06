======================
django_excel_templates
======================

Django MS Excel Generator aims to create a template system for generation of
the Excel documents for views (instead of HTML).


1. **Simple case**: sniff model and make an excel table; 
2. **Medium case**: sniff model, make excel table, and apply predetermined styles (fonts, colors, layout)
3. **Advanced case**: take models and set custom styles or modify existing


Requiments
----------
 
 * `Python 2.4+ \< 3.0 <http://www.python.org>`_
 * `Django <http://www.djangoproject.com>`_
 * `xlwt >= 0.7.2 <http://pypi.python.org/pypi/xlwt>`_


Install
-------

You have two options:

1. Easy_insall with install the package and all dependencies if they aren't already installed into your lib/python/::

     easy_install django_excel_templates 

2. Download and untar the package; run::

     python setup.py install


Examples
--------

``testobj`` in the following examples is django.db.models.query.QuerySet instance

**Simple**:
create ExcelReport instance, add excel sheet, add queryset to analyze:

    >>> from django_excel_templates import *
    >>> report = ExcelReport()
    >>> report.addSheet("TestBasic")
    >>> report.addQuerySet(testobj, REPORT_HORZ, addheader=True)


**Medium** (create styles, one by one):
create ExcelStyle instance to specify style (see help(ExcelStyle) for available methods and style options),
create ExcelFormatter instance, add style to it:

    >>> report.addSheet("TestStyle")
    >>> style = ExcelStyle() 
    >>> style.set_alignment(horz=3, wrap=1)
    >>> style.set_font(font_color='000000', bold=True, italic=True)
    >>> style.set_border(border_color='000000', border_style=5)
    >>> style.set_pattern(pattern_color='339933', pattern=1)
    >>> formatter = ExcelFormatter()
    >>> formatter.addBodyStyle(style=style)
    >>> report.addFormatter(formatter)
    >>> report.addQuerySet(testobj, orientation=REPORT_HORZ, addheader=True)


**Medium** (create styles all at once):

    >>> report.addSheet("TestStyle2")
    >>> headerstyle = ExcelStyle(font_color='00FF00', shadow=True, underline=True, 
    		      		 pattern_color='000000', pattern=1, border_style=5, 
				 border_color='FFFFFF')
    >>> col_style = ExcelStyle(font_color='FFFFFF')
    >>> formatter.addHeaderStyle(headerstyle)
    >>> formatter.addColunmStyle('column_name', style=col_style)
    >>> report.addQuerySet(testobj, REPORT_HORZ, True)


**Advanced**:
change existing styles, set custom styles, adjust column style and width:

    >>> report.addSheet("ModifyStyle")
    >>> style.set_font(font_color='000000', bold=False, underline=True)
    >>> style.set_border(border_color='330099', border_style=6)
    >>> style.set_pattern(pattern_color='FFFFFF', pattern=1)
    >>> colstyle.set_pattern(pattern_color='FFFF33', pattern=1)
    >>> formatter.setWidth('column1_name, column2_name', width=600)
    >>> report.addQuerySet(testobj, REPORT_HORZ, True)


To make django.http.HttpResponse out of ``report`` and tell the broswer to treat it as an excel attachment:

    >>> response = HttpResponse(report.writeReport(), mimetype='application/ms-excel')
    >>> response['Content-Disposition'] = 'attachment; filename=foo.xls' 
