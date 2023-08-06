# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.render import render
from noc.lib.registry import Registry
from noc.lib.svg import has_svg_support,vertical_text_inline
from django.conf import settings

#
admin_media_prefix=settings.ADMIN_MEDIA_PREFIX

##
##
##
class ReportRegistry(Registry):
    name="ReportRegistry"
    subdir="reports"
    classname="Report"
report_registry=ReportRegistry()


##
## Report Columns
## 'format' is a function accepting value and returning valid html code
##
class Column(object):
    def __init__(self,name,align=None,v_align=None,format=None):
        self.name=name
        self.align=align
        self.v_align=v_align
        self.format=format
        
    def render_header(self):
        return "<TH>%s</TH>"%self.name
        
    def render_cell(self,value):
        if self.format:
            value=self.format(value)
        flags=[]
        if self.align:
            flags+=["ALIGN='%s'"%self.align]
        if self.v_align:
            flags+=["VALIGN='%s'"%self.v_align]
        if flags:
            flags=" "+" ".join(flags)
        else:
            flags=""
        return "<TD%s>%s</TD>"%(flags,value)
##
## Boolean field rendered as checkmark
##
class BooleanColumn(Column):
    def render_cell(self,value):
        if value:
            url=admin_media_prefix+"img/admin/icon-yes.gif"
        else:
            url=admin_media_prefix+"img/admin/icon-no.gif"
        return "<TD><IMG SRC='%s' /></TD>"%url

##
##
##
class ReportBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        report_registry.register(m.name,m)
        return m
##
## Abstract Report
##
class Report(object):
    __metaclass__=ReportBase
    name=None
    form_class=None # Or forms.form descendant
    template="main/report.html"
    title="Generic Report"
    requires_cursor=False
    columns=[]
    refresh=None # Time to refresh report (in seconds)
    
    def __init__(self,request,query=None):
        self.request=request
        self.query=query
        if self.form_class:
            if self.query:
                self.form=self.form_class(query)
            else:
                self.form=self.form_class()
        else:
            self.form=None
        if self.requires_cursor:
            from django.db import connection
            self.cursor = connection.cursor()
            
    def is_valid(self):
        return self.form is None or self.form.is_valid()
    
    def render(self):
        out="<TABLE SUMMARY='%s'>"%self.title
        out+="<TR>"+"".join([c.render_header() for c in self.columns])+"</TR>"
        n=0
        for row in self.get_queryset():
            out+="<TR CLASS='row%d'>"%((n%2)+1)+"".join([c.render_cell(v) for c,v in zip(self.columns,row)])+"</TR>"
            n+=1
        out+="</TABLE>"
        return render(self.request,self.template,{"report":self,"query":self.query,"data":out,"refresh":self.refresh})
            
    def get_queryset(self):
        return []
        
    def execute(self,sql,args=[]):
        self.cursor.execute(sql,args)
        return self.cursor.fetchall()
##
## Matrix report
##
## get_queryset must return a triple of (column-label,row-label,value)
class MatrixReport(Report):
    def render(self):
        def column_label_svg(s):
            return vertical_text_inline(s)
        def column_label_html(s):
            return "<BR/>".join(s)
        if has_svg_support(self.request):
            column_label=column_label_svg
        else:
            column_label=column_label_html
        data={}
        cl={}
        rl={}
        for c,r,v in self.get_queryset():
            data[c,r]=v
            cl[c]=None
            rl[r]=None
        cl=sorted(cl.keys())
        rl=sorted(rl.keys())
        out="<TABLE SUMMARY='%s' BORDER='1'>"%self.title
        out+="<TR><TH></TH>%s</TR>"%"".join(["<TH>%s</TH>"%column_label(c) for c in cl])
        n=0
        for r in rl:
            out+="<TR CLASS='row%d'><TD><B>%s</B></TD>"%((n%2)+1,r)
            for c in cl:
                try:
                    out+="<TD>%s</TD>"%data[c,r]
                except KeyError:
                    out+="<TD>&nbsp;</TD>"
            out+="</TR>"
            n+=1
        out+="</TABLE>"
        return render(self.request,self.template,{"report":self,"query":self.query,"data":out})
