#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2008-9  Iñigo Serna
# Time-stamp: <2009-09-25 13:55:18 inigo>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


u"""agenda2pdf.py - (C) 2008-9, by Iñigo Serna

This program generates a book agenda file in PDF format file.
I've created it for using with iLiad eBook reader
(http://www.irextechnologies.com/products/iliad).
Released under GNU Public License, read COPYING for more details.

Usage:\tpython agenda2pdf.py <options>

Options:
    -h, --help            Show this text
    -v, --version         Show version and exit
    -y, --year            Year. If not specified current year is used
    -w, --first-week-day  First day of week: 0 = monday, 6 = sunday
                          (default: 0, monday)
    -f, --format          Sections to build. Consult documentation for the
                          definition of each type (default: ciypmwPb)
    -o, --output          PDF Output file (default: "agenda-yyyy.pdf")
    -s, --page-size       Specify page size.
                          Valid options: A4, A5, A6, LEGAL, LETTER, ILIAD,
                          ILIAD_FULLSCREEN, ORGANIZER (default: A4)
    -c, --no-compression  Disable PDF file compression (default: enabled)
    -q, --quiet           Don't output messages on screen
"""


__author__ = 'Iñigo Serna'
__revision__ = '1.0'


import sys
import calendar
from datetime import date
import getopt

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LEGAL, LETTER, A5, A6
from reportlab.lib.colors import lightcoral, black, grey, navy


######################################################################
##### some variables and default values
FIRST_WEEK_DAY = 0 # monday
YEAR = 2009
OUTPUT_PRE = 'agenda-'
ILIAD_SIZE = (124, 152) # iLiad with toolbar
ILIAD_SIZE_FULLSCREEN = (124, 164) # iLiad fullscreen
ORGANIZER = (270,486) # FiloFax Organizer, courtesy of Tony Foley
PAGE_SIZES = {'A4': A4, 'A5': A5, 'A6': A6, 'LEGAL': LEGAL, 'LETTER': LETTER,
              'ILIAD': ILIAD_SIZE, 'ILIAD_FULLSCREEN': ILIAD_SIZE_FULLSCREEN,
              'ORGANIZER': ORGANIZER }
SIZE = A4
COVER_IMG = './cover.jpg'
DEFAULT_FORMAT = 'ciypmwPb'
# COPYRIGHT_STRING = u'(C) %d, Iñigo Serna' % YEAR
COPYRIGHT_STRING = u'https://inigo.katxi.org/devel/agenda2pdf'

SECTIONS = { 'c': ('cover', 'cover(c, cfg.year)', None),
             'b': ('back', 'back(c)', None),
             'B': ('blank', 'blank(c)', None),
             'i': ('index', 'year_view(c, cfg.year)', 'index'),
             'y': ('3 years', 'year_3view(c, cfg.year)', '3_years'),
             'p': ('planner', 'planner_view(c, cfg.year)', 'planner_%d/1'),
             'P': ('planner next year', 'planner_view(c, cfg.year+1, False)', 'planner_%d/1'),
             'm': ('2 months', 'month_2view(c, cfg.year)', 'month2_%d/1'),
             'M': ('1 month', 'month_1view(c, cfg.year)', 'month_%d/1'),
             'w': ('agenda half week', 'agenda_halfweek_view(c, cfg.year)', 'agenda_halfweek_%d/1'),
             'W': ('agenda week', 'agenda_wholeweek_view(c, cfg.year)', 'agenda_week_%d/1'),
             'd': ('agenda day', 'day_view(c, cfg.year)', 'agenda_day_%d/1/1'),
             'D': ('agenda day+blank', 'day_view(c, cfg.year, True)', 'agenda_day_%d/1/1') }

# globals
w, h, f = 0, 0, 0  # page width, page height, scale factor
wds = [d[:2] for d in calendar.day_abbr]
cal = None
cfg = None


######################################################################
##### CANVAS
def prepare_canvas(year):
    global w, h, f
    c = canvas.Canvas(cfg.output, pagesize=cfg.size,
                      pageCompression=cfg.compression)
    c.setTitle('Agenda %d' % year)
    c.setSubject('Agenda %d' % year)
    c.setAuthor(u'Iñigo Serna')
    c.setKeywords(('agenda', str(year)))
    w, h = cfg.size
    f = w / A4[0]
    return c


######################################################################
##### COMMON CONTENTS
def add_pagenumber(c):
    c.setFont('Times-Roman', 8*f)
    c.setFillColor(grey)
    c.drawCentredString(w/2, 2*f, '- Page %d. -' % c.getPageNumber())
    if 'i' in cfg.format:
        c.linkAbsolute('ToC', 'index', (w/2-20*f, 0, w/2+20*f, 10*f))


def add_copyright(c):
    if cfg.copyright:
        c.setFont('Times-Roman', 8*f)
        c.setFillColor(grey)
        c.drawRightString(w-2*f, 2*f, COPYRIGHT_STRING)


######################################################################
##### COVER
def cover(c, year):
    c.drawImage(COVER_IMG, 0, 0, width=w, height=h)
    c.setLineWidth(7*f)
    c.setStrokeColorRGB(0.3, 0.23, 0.23)
    c.setFillColorRGB(0.6, 0.46, 0.46)
    c.rect((w-250*f)/2, h-140*f, 250*f, -150*f, fill=1)
    c.setFont('Helvetica-Bold', 60*f)
    c.setFillColorRGB(0.1, 0.05, 0.05)
    c.drawCentredString(w/2, h-200*f, 'Agenda')
    c.drawCentredString(w/2, h-270*f, '%d' % year)
    add_copyright(c)
    c.showPage()

    
def back(c):
    c.drawImage(COVER_IMG, 0, 0, width=w, height=h)
    add_copyright(c)
    c.showPage()
    

def blank(c):
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


######################################################################
##### YEAR VIEW
def year_view(c, year, toc=True):
    # page header
    c.setFont('Helvetica-Bold', 22*f)
    c.setFillColor(lightcoral)
    c.drawString(10*f, h-35*f, '%d' % year)
    c.setStrokeColor(lightcoral)
    c.setLineWidth(4*f)
    c.line(10*f, h-45*f, w-10*f, h-45*f)

    # calc values
    margin = 15*f
    spacing = 20*f
    w2 = (w-2*margin-2*spacing) / 3.0
    w3 = w2 / 7.0
    xpos = (margin, w/2-w2/2, w-margin-w2)
    h2 = h - 80*f
    ypos = (h-80*f, h-220*f, h-360*f, h-500*f)

    # months
    for m in xrange(12):
        y = ypos[int(m/3)]
        # month header
        x = xpos[m%3] + w2/2
        c.setFont('Times-Bold', 17*f)
        c.setFillColor(lightcoral)
        c.drawCentredString(x, y, calendar.month_name[m+1].upper())
        if 'm' in cfg.format:
            c.linkAbsolute('Month %d/%d' % (year, m+1),
                           'month2_%d/%d' % (year, m+1),
                           (x-100*f, y-120*f, x+100*f, y+20*f))
        elif 'M' in cfg.format:
            c.linkAbsolute('Month %d/%d' % (year, m+1),
                           'month_%d/%d' % (year, m+1),
                           (x-100*f, y-120*f, x+100*f, y+20*f))
        # day of week
        x = xpos[m%3]
        y -= 20*f
        c.setFont('Helvetica-Bold', 11*f)
        c.setFillColor(black)
        for i, d in enumerate(cal.iterweekdays()):
            c.drawCentredString(x+i*w3+w3/2, y, calendar.day_abbr[d])
        # days
        c.setFont('Helvetica', 12*f)
        for week in cal.monthdays2calendar(year, m+1):
            y -= 15*f
            for i, (day, dw) in enumerate(week):
                if day == 0:
                    continue
                color = grey if dw < 5 else navy
                c.setFillColor(color)
                c.drawRightString(x+i*w3+w3/1.2, y, '%2d' % day)

    # Table of Contents
    if toc:
        # header 
        c.setFont('Helvetica-Bold', 22*f)
        c.setFillColor(lightcoral)
        c.drawString(10*f, 140*f, 'Table of Contents')
        c.setStrokeColor(lightcoral)
        c.setLineWidth(4*f)
        c.line(10*f, 130*f, w-10*f, 125*f)
        # links
        c.setFont('Times-Roman', 18*f)
        c.setFillColor(black)
        x0 = x = 100*f
        y0 = y = 100*f
        for it in cfg.format:
            if it in SECTIONS.keys():
                link = SECTIONS[it][2]
                if link is not None:
                    if it == 'p':
                        title = 'Planner %d' % year
                        link = link % year
                    elif it == 'P':
                        title = 'Planner %d' % (year+1)
                        link = link % (year+1)
                    elif it in ('m', 'M', 'w', 'W', 'd', 'D'):
                        title = SECTIONS[it][0].capitalize()
                        link = link % year
                    else:
                        title = SECTIONS[it][0].capitalize()
                        link = link
                    if y < 25*f:
                        x, y = x+150*f, y0
                    c.drawString(x, y, '* ' + title)
                    c.linkAbsolute(title, link, (x, y-5*f, x+150*f, y+15*f))
                    y -= 22*f
    # write page
    c.bookmarkPage('index')
    c.bookmarkPage('year_%d' % year)
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def minical_year(c, year, y0):
    # header
    c.setFont('Helvetica-Bold', 18*f)
    c.setFillColor(lightcoral)
    c.setStrokeColor(lightcoral)
    c.setLineWidth(2*f)
    c.drawString(10*f, y0, '%d' % year)
    if 'i' in cfg.format:
        c.linkAbsolute('Index', 'index', (0, y0-5*f, w, y0+15*f))
    c.line(10*f, y0-5*f, w-10*f, y0-5*f)

    # calc values
    margin = 10*f
    spacing = 15*f
    w2 = (w-2*margin-3*spacing) / 4.0
    w3 = w2 / 7.0
    xpos = (margin, margin+w2+spacing, margin+2*w2+2*spacing, margin+3*w2+3*spacing)
    ypos = (y0-20*f, y0-100*f, y0-180*f)

    # months
    for m in xrange(12):
        y = ypos[int(m/4)]
        # month header
        c.setFont('Times-Bold', 13*f)
        c.setFillColor(lightcoral)
        c.drawCentredString(xpos[m%4]+w2/2, y, calendar.month_name[m+1].upper())
        # day of week
        x = xpos[m%4]
        y -= 10*f
        c.setFont('Helvetica-Bold', 8*f)
        c.setFillColor(black)
        for i, d in enumerate(cal.iterweekdays()):
            c.drawCentredString(x+i*w3+w3/2, y, calendar.day_abbr[d][:2])
        # days
        c.setFont('Helvetica', 9*f)
        for week in cal.monthdays2calendar(year, m+1):
            y -= 9*f
            for i, (day, dw) in enumerate(week):
                if day == 0:
                    continue
                color = grey if dw < 5 else navy
                c.setFillColor(color)
                c.drawRightString(x+i*w3+w3/1.2, y, '%2d' % day)


def year_3view(c, year):
    minical_year(c, year-1, h-20*f)
    minical_year(c, year, 2*h/3.0-20*f)
    minical_year(c, year+1, h/3.0-20*f)
    c.bookmarkPage('3_years')
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


######################################################################
##### MONTH VIEW
def render_minical_month(c, year, month, xpos, ypos, w3, h3, y):
    c.setFont('Helvetica-Bold', 13*f)
    c.setFillColor(black)
    c.setLineWidth(1*f)
    for i, d in enumerate(cal.iterweekdays()):
        c.drawCentredString(xpos[i]+w3/2, y, calendar.day_name[d])
    for j, week in enumerate(cal.monthdays2calendar(year, month)):
        aday = week[0][0] if week[0][0] != 0 else week[6][0]
        weeknum = date(year, month, aday).isocalendar()[1]
        if 'd' in cfg.format or 'D' in cfg.format:
            wlw = xpos[0]
        else:
            wlw = w3*8
        if 'w' in cfg.format:
            c.linkRect('Agenda HalfWeek %d/%d' % (year, weeknum),
                       'agenda_halfweek_%d/%d' % (year, weeknum),
                       (0, ypos[j], wlw, ypos[j]+h3))
        elif 'W' in cfg.format:
            c.linkRect('Agenda Week %d/%d' % (year, weeknum),
                       'agenda_week_%d/%d' % (year, weeknum),
                       (0, ypos[j], wlw, ypos[j]+h3))
        c.setFont('Times-Roman', 12*f)
        c.setFillColor(black)
        c.drawString(10*f, ypos[j]+h3/2, str(weeknum))
        c.setFont('Helvetica-Bold', 15*f)
        for i, (d, dw) in enumerate(week):
            if d == 0:
                continue
            c.setFillColorRGB(0.8, 0.8, 0.8)
            fill = 1 if dw > 4 else 0
            c.rect(xpos[i], ypos[j], w3, h3, fill=fill)
            c.setFillColor(navy)
            c.drawRightString(xpos[i]+w3-5*f, ypos[j]+h3-15*f, str(d))
            if 'd' in cfg.format or 'D' in cfg.format:
                c.linkRect('Agenda Day %d/%d/%d' % (year, month, d),
                           'agenda_day_%d/%d/%d' % (year, month, d),
                           (xpos[i], ypos[j], xpos[i]+w3, ypos[j]+h3))


# month view: 1 month landscape
def months_1month_landscape(c, year, month):
    # rotate page
    c.saveState()
    hh, ww = w, h
    c.rotate(90)
    # page header
    c.setFont('Helvetica-Bold', 22*f)
    c.setFillColor(lightcoral)
    c.drawCentredString(ww/2, -30*f, '%s %d' % (calendar.month_name[month], year))
    if 'i' in cfg.format:
        c.linkRect('Index', 'index', (ww/2-100*f, 0, ww/2+100*f, -50*f))
    # calc values
    cal_rowsnum = len(cal.monthdayscalendar(year, month))
    ww_margin = 35*f
    hh_margin_top = 65*f
    hh_margin_bottom = 15*f
    ww2 = (ww-2*ww_margin) / 7.0
    hh2 = (hh-hh_margin_top-hh_margin_bottom) / float(cal_rowsnum)
    xpos = [ww_margin+i*ww2 for i in range(7)]
    ypos = [-(hh_margin_top+(i+1)*hh2) for i in range(cal_rowsnum)]
    # contents
    render_minical_month(c, year, month, xpos, ypos, ww2, hh2, -55*f)
    # write page
    c.restoreState()
    c.bookmarkPage('month_%d/%d' % (year, month))
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def minical_month(c, year, month, y0):
    # page header
    c.setFont('Helvetica-Bold', 22*f)
    c.setFillColor(lightcoral)
    c.drawCentredString(w/2, y0-25*f, '%s %d' % (calendar.month_name[month], year))
    if 'i' in cfg.format:
        c.linkRect('Index', 'index', (w/2-100*f, y0, w/2+100*f, y0-30*f))
    # calc values
    cal_rowsnum = len(cal.monthdayscalendar(year, month))
    w_margin = 35*f
    h_margin_top = 60*f
    h_margin_bottom = 10*f
    w2 = (w-2*w_margin) / 7.0
    h2 = (h/2-h_margin_top-h_margin_bottom) / (cal_rowsnum+1.0)
    xpos = [w_margin+i*w2 for i in range(7)]
    ypos = [y0-h_margin_top-(i+1)*h2 for i in range(cal_rowsnum)]
    # contents
    render_minical_month(c, year, month, xpos, ypos, w2, h2, y0-50*f)


# month view: 2 months vertical
def months_2month_vertical(c, year, month):
    minical_month(c, year, month, h)
    minical_month(c, year, month+1, h/2)
    c.bookmarkPage('month2_%d/%d' % (year, month))
    c.bookmarkPage('month2_%d/%d' % (year, month+1))
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


# month view
def month_1view(c, year):
    for m in range(12):
        months_1month_landscape(c, year, m+1)


def month_2view(c, year):
    for m in range(6):
        months_2month_vertical(c, year, m*2+1)


######################################################################
##### PLANNER VIEW
def planner_3months(c, year, first_month, links):
    # calc values
    d1, dmax1 = calendar.monthrange(year, first_month)
    d2, dmax2 = calendar.monthrange(year, first_month+1)
    d3, dmax3 = calendar.monthrange(year, first_month+2)
    w2 = (w-60*f) / 3.0
    step = (h-40*f) / 32.0

    # headers
    c.setFont('Helvetica-Bold', 20*f)
    c.setFillColor(lightcoral)
    c.drawCentredString(w/2, h-24*f, 'Planning %d' % year)
    if 'i' in cfg.format:
        c.linkAbsolute('Index', 'index', (w/2-80*f, h-30*f, w/2+80*f, h-5*f))
    c.setFont('Times-Bold', 15*f)
    c.setFillColor(navy)
    c.drawString(35*f, h-46*f, '%s %d' % (calendar.month_name[first_month], year))
    c.drawString(35*f+w2, h-46*f, '%s %d' % (calendar.month_name[first_month+1], year))
    c.drawString(35*f+2*w2, h-46*f, '%s %d' % (calendar.month_name[first_month+2], year))
    if links:
        if 'm' in cfg.format:
            c.linkAbsolute('Months %d/%d' % (year, first_month),
                           'month2_%d/%d' % (year, first_month),
                           (30*f, h-55*f, 30*f+w2, h-55*f+step))
            c.linkAbsolute('Months %d/%d' % (year, first_month+1),
                           'month2_%d/%d' % (year, first_month+1),
                           (30*f+w2, h-55*f, 30*f+2*w2, h-55*f+step))
            c.linkAbsolute('Months %d/%d' % (year, first_month+2),
                           'month2_%d/%d' % (year, first_month+2),
                           (30*f+2*w2, h-55*f, 30*f+3*w2, h-55*f+step))
        elif 'M' in cfg.format:
            c.linkAbsolute('Months %d/%d' % (year, first_month),
                           'month_%d/%d' % (year, first_month),
                           (30*f, h-55*f, 30*f+w2, h-55*f+step))
            c.linkAbsolute('Months %d/%d' % (year, first_month+1),
                           'month_%d/%d' % (year, first_month+1),
                           (30*f+w2, h-55*f, 30*f+2*w2, h-55*f+step))
            c.linkAbsolute('Months %d/%d' % (year, first_month+2),
                           'month_%d/%d' % (year, first_month+2),
                           (30*f+2*w2, h-55*f, 30*f+3*w2, h-55*f+step))

    # contents
    c.setFont('Times-Roman', 13*f)
    c.setStrokeColor(black)
    c.setLineWidth(1*f)
    for i in range(32):
        y = h - 30*f - (i+1)*step
        c.line(5*f, y+step, w-5*f, y+step)
        dd1, dd2, dd3 = (d1+i-1) % 7, (d2+i-1) % 7, (d3+i-1) % 7
        fill1 = 1 if dd1 > 4 and 1 <= i <= dmax1 else 0
        fill2 = 1 if dd2 > 4 and 1 <= i <= dmax2 else 0
        fill3 = 1 if dd3 > 4 and 1 <= i <= dmax3 else 0
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.rect(30*f, y, w2, step, fill=fill1)
        c.rect(30*f+w2, y, w2, step, fill=fill2)
        c.rect(30*f+2*w2, y, w2, step, fill=fill3)
        if i != 0:
            c.setFillColor(navy)
            c.drawRightString(25*f, y+7*f, str(i))
            c.drawRightString(w-10*f, y+7*f, str(i))
            c.setFillColor(grey)
            if i <= dmax1:
                c.drawString(35*f, y+7*f, wds[dd1])
            if i <= dmax2:
                c.drawString(35*f+w2, y+7*f, wds[dd2])
            if i <= dmax3:
                c.drawString(35*f+2*w2, y+7*f, wds[dd3])

    # create lines
    c.rect(5*f, 10*f, w-10*f, h-15*f)
    c.line(55*f, 10*f, 55*f, h-30*f-step)
    c.line(55*f+w2, 10*f, 55*f+w2, h-30*f-step)
    c.line(55*f+2*w2, 10*f, 55*f+2*w2, h-30*f-step)

    # write page
    c.bookmarkPage('planner_%d/%d' % (year, first_month))
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def planner_view(c, year, links=True):
    planner_3months(c, year, 1, links)
    planner_3months(c, year, 4, links)
    planner_3months(c, year, 7, links)
    planner_3months(c, year, 10, links)


######################################################################
##### AGENDA COMMON
def __get_prevweek(year, month):
    if month == 1:
        y = year-1; m = 12
    else:
        y = year; m = month-1
    prevweek = cal.monthdayscalendar(y, m)[-1]
    return [(d, 0) for d in prevweek], m, y


def __get_nextweek(year, month):
    if month < 12:
        y = year; m = month+1
    else:
        y = year+1; m = 1
    nextweek = cal.monthdayscalendar(y, m)[0]
    return [(d, 0) for d in nextweek], m, y


def nanocal_month(c, year, month, x, y, w2, thismonth, fontsize, links=True):
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setFillColorRGB(0.8, 0.8, 0.8)
    if thismonth:
        h2 = len(cal.monthdayscalendar(year, month)) + 1
        c.rect(x, y+fontsize, w2, -h2*(fontsize+f), fill=1)
    if 'm' in cfg.format and links:
        c.linkRect('Month %d/%d' % (month, year), 'month2_%d/%d' % (year, month),
                   (x, y+fontsize, x+w2, y-7*fontsize))
    elif 'M' in cfg.format and links:
        c.linkRect('Month %d/%d' % (month, year), 'month_%d/%d' % (year, month),
                   (x, y+fontsize, x+w2, y-7*fontsize))

    # month header
    c.setFont('Courier-Bold', fontsize)
    c.setFillColor(grey)
    c.setLineWidth(1*f)
    c.setStrokeColor(grey)
    c.drawCentredString(x+w2/2, y, calendar.month_name[month])
    c.line(x, y-2*f, x+w2, y-2*f)

    # days
    x, y = x+f, y-2*f
    c.setFont('Courier', fontsize)
    for week in cal.monthdays2calendar(year, month):
        y = y - fontsize
        for i, (d, dw) in enumerate(week):
            if d == 0:
                continue
            color = grey if dw < 5 else navy
            c.setFillColor(color)
            c.drawString(x+i*w2/7.0, y, '%2d' % d)


def minical_halfyear(c, year, x, y, w, current_month, firstmonth=1, halfweek=False):
    fontsize = 9*f if halfweek else 6*f
    w2 = (w-5*fontsize/2) / 6.0
    xpos = [x+(w2+4*f)*i for i in range(6)]
    for m in range(6):
        thismonth = True if current_month == m+firstmonth else False
        nanocal_month(c, year, m+firstmonth, xpos[m], y, w2, thismonth, fontsize)


######################################################################
##### AGENDA WHOLEWEEK
def draw_agenda_wholeweek_landscape(c, year, monthnum, ww, hh, ww_margin, ww2,
                                    m1, y1, m2, y2, weeknum, week, xpos):
    # rotate page
    c.saveState()
    c.rotate(90)

    # page header
    c.setStrokeColor(lightcoral)
    c.setFont('Helvetica', 12*f)
    c.setFillColor(lightcoral)
    c.drawString(ww_margin, -15*f, '%s %d' % (calendar.month_name[m1], y1))
    c.drawString(ww/2+10*f, -15*f, 'Week: %d' % weeknum)
    c.drawRightString(ww-ww_margin, -15*f,
                      '%s %d' % (calendar.month_name[m2], y2))
    if 'i' in cfg.format:
        c.linkRect('Index', 'index', (0, 0, ww, -20*f))

    # main division lines
    c.setLineWidth(2*f)
    c.line(ww_margin, -20*f, ww/2-ww_margin, -20*f)
    c.line(ww/2+ww_margin, -20*f, ww-ww_margin, -20*f)
    c.line(ww_margin, -100*f, ww/2-ww_margin, -100*f)
    c.line(ww/2+ww_margin, -100*f, ww-ww_margin, -100*f)
    c.line(ww_margin, -(hh-140*f), ww/2-ww_margin, -(hh-140*f))
    c.line(ww/2+ww_margin, -(hh-140*f), ww-ww_margin, -(hh-140*f))
    c.line(ww_margin, -(hh-65*f), ww/2-ww_margin, -(hh-65*f))
    c.line(ww/2+ww_margin, -(hh-65*f), ww-ww_margin, -(hh-65*f))
    c.setStrokeColor(navy)
    c.line(ww_margin, -60*f, ww/2-ww_margin, -60*f)
    c.line(ww/2+ww_margin, -60*f, ww-ww_margin, -60*f)

    # lines above diary
    c.setLineWidth(1*f)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    step = 40*f / 3.0
    y = -60*f - step
    for i in range(2):
        c.line(ww_margin, y-i*step, ww/2-ww_margin, y-i*step)
        c.line(ww/2+ww_margin, y-i*step, ww-ww_margin, y-i*step)

    # lines in diary
    step = (hh-240*f) / 27.0
    c.setFillColor(navy)
    c.setFont('Times-Roman', 8*f)
    for i in range(27-1):
        y = -100*f-step*(i+1)
        c.line(ww_margin, y, ww/2-ww_margin, y)
        if i <= 13:
            c.line(ww/2+ww_margin, y, ww-ww_margin, y)
        else:
            c.line(ww/2+ww_margin, y, xpos[4]+ww2, y)
        if i%2 == 0:
            for j in range(6):
                if j == 5 and i > 13:
                    break
                c.drawRightString(xpos[j]+8*f, y+3*f, str(i/2+8))
    for i in range(9): # complete sunday
        y = -100*f - step*(14+4+i)
        c.line(xpos[5], y, ww-ww_margin, y)

    # lines above minicalendars
    step = 75*f / 5.0
    y = -(hh-140*f) - step
    for i in range(4):
        c.line(ww_margin, y-i*step, ww/2-ww_margin, y-i*step)
        c.line(ww/2+ww_margin, y-i*step, ww-ww_margin, y-i*step)

    # day
    c.setFillColor(navy)
    for i, (d, dw) in enumerate(week):
        c.setFont('Times-Roman', 40*f)
        c.drawString(xpos[i], -55*f, str(d))
        c.setFont('Times-Roman', 15*f)
        c.drawString(xpos[i]+45*f, -55*f, calendar.day_name[dw])
    y = -100*f - step*(14+1)
    c.setLineWidth(2*f)
    c.setStrokeColor(navy)
    c.line(xpos[5], y, ww-ww_margin, y)
    c.setFont('Times-Roman', 40*f)
    c.setFillColor(navy)
    c.drawString(xpos[5], y+5*f, str(week[6][0]))
    c.setFont('Times-Roman', 15*f)
    c.drawString(xpos[5]+45*f, y+5*f, calendar.day_name[week[6][1]])

    # page bottom: minicalendars
    ww2 = ww/2 - 2*ww_margin
    y = -hh + 50*f
    minical_halfyear(c, year, ww_margin, y, ww2, monthnum+1, 1, halfweek=False)
    minical_halfyear(c, year, ww/2+ww_margin, y, ww2, monthnum+1, 7, halfweek=False)

    # write page
    c.restoreState()
    c.bookmarkPage('agenda_week_%d/%d' % (year, weeknum))
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def agenda_wholeweek_view(c, year):
    wholeyear = [cal.monthdays2calendar(year, m+1) for m in range(12)]
    weeknum = 0

    # calc values
    hh, ww = w, h
    ww_margin = 10*f
    ww_spacing = 10*f
    ww2 = (ww-2*ww_margin-5*ww_spacing) / 6.0
    xpos = [ww_margin+i*(ww2+ww_spacing) for i in range(7)]

    # show week
    skipnext = False
    for monthnum, month in enumerate(wholeyear):
        m1, y1 = m2, y2 = monthnum+1, year
        for week in month:
            if skipnext:
                skipnext = False
                continue
            weeknum += 1
            if weeknum == 1 and week[0][0] == 0: # beginning of year
                nw, m1, y1 = __get_prevweek(year, monthnum+1)
                week = [(week[i][0]+nw[i][0], week[i][1]+nw[i][1]) for i in range(7)]
            else:
                m1, y1 = monthnum+1, year
            if week[6][0] == 0: # end of month
                nw, m2, y2 = __get_nextweek(year, monthnum+1)
                week = [(week[i][0]+nw[i][0], week[i][1]+nw[i][1]) for i in range(7)]
                skipnext = True
            draw_agenda_wholeweek_landscape(c, year, monthnum, ww, hh, ww_margin, ww2,
                                            m1, y1, m2, y2, weeknum, week, xpos)


######################################################################
##### AGENDA HALFWEEK
def draw_agenda_halfweek_common(c, year, monthnum, weeknum, week, firstmonth,
                                w, h, w_margin):
    if 'i' in cfg.format:
        c.linkRect('Index', 'index', (0, h, w, h-25*f))

    # main division lines
    c.setStrokeColor(lightcoral)
    c.setLineWidth(3*f)
    c.line(w_margin, h-30*f, w-w_margin, h-30*f)
    c.line(w_margin, h-130*f, w-w_margin, h-130*f)
    c.line(w_margin, 170*f, w-w_margin, 170*f)
    c.line(w_margin, 85*f, w-w_margin, 85*f)
    c.setStrokeColor(navy)
    c.line(w_margin, h-80*f, w-w_margin, h-80*f)

    # lines above diary
    c.setLineWidth(1*f)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    step = 50*f / 3.0
    y = h-80*f - step
    for i in range(2):
        c.line(w_margin, y-i*step, w-w_margin, y-i*step)
  
    # lines above minicalendars
    step = 85*f / 5.0
    y = 170*f - step
    for i in range(4):
        c.line(w_margin, y-i*step, w-w_margin, y-i*step)

    # page bottom: minicalendars
    w2 = w - 2*w_margin
    y = 65*f
    minical_halfyear(c, year, w_margin, y, w2, monthnum+1, firstmonth, halfweek=True)

    # write page
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def draw_agenda_halfweek_1(c, year, m1, y1, weeknum, monthnum, week,
                           w, h, w_margin, xpos):
    # page header
    c.setStrokeColor(lightcoral)
    c.setFont('Helvetica', 17*f)
    c.setFillColor(lightcoral)
    c.drawString(w_margin, h-20*f, '%s %d' % (calendar.month_name[m1], y1))
    c.drawRightString(w-w_margin, h-20*f, 'Week: %d' % weeknum)

    # lines in diary
    c.setLineWidth(1*f)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    step = (h-300*f) / 27.0
    c.setFillColor(navy)
    c.setFont('Times-Roman', 8*f)
    for i in range(27-1):
        y = (h-130*f)-step*(i+1)
        c.line(w_margin, y, w-w_margin, y)
        if i%2 == 0:
            for j in range(3):
                c.drawRightString(xpos[j]+8*f, y+3*f, str(i/2+8))
    
    # day
    c.setFillColor(navy)
    for i, (d, dw) in enumerate(week[:3]):
        c.setFont('Times-Roman', 45*f)
        c.drawString(xpos[i], h-72*f, str(d))
        c.setFont('Times-Roman', 24*f)
        c.drawString(xpos[i]+55*f, h-72*f, calendar.day_name[dw])

    # end
    c.bookmarkPage('agenda_halfweek_%d/%d' % (year, weeknum))
    draw_agenda_halfweek_common(c, year, monthnum, weeknum, week, 1,
                                w, h, w_margin)


def draw_agenda_halfweek_2(c, year, m2, y2, weeknum, monthnum, week,
                           w, h, w_margin, xpos, w2):
    # page header
    c.setStrokeColor(lightcoral)
    c.setFont('Helvetica', 17*f)
    c.setFillColor(lightcoral)
    c.drawString(w_margin, h-20*f, 'Week: %d' % weeknum)
    c.drawRightString(w-w_margin, h-20*f, '%s %d' % (calendar.month_name[m2], y2))

    # lines in diary
    c.setLineWidth(1*f)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    step = (h-300*f) / 27.0
    c.setFillColor(navy)
    c.setFont('Times-Roman', 8*f)
    for i in range(27-1):
        y = (h-130*f)-step*(i+1)
        if i <= 13:
            c.line(w_margin, y, w-w_margin, y)
        else:
            c.line(w_margin, y, xpos[1]+w2, y)
        if i%2 == 0:
            for j in range(3):
                if j == 2 and i > 13:
                    break
                c.drawRightString(xpos[j]+8*f, y+3*f, str(i/2+8))
    for i in range(9): # complete sunday
        y = h-130*f - step*(14+4+i)
        c.line(xpos[2], y, w-w_margin, y)

    # day
    c.setFillColor(navy)
    for i, (d, dw) in enumerate(week[3:6]):
        c.setFont('Times-Roman', 45*f)
        c.drawString(xpos[i], h-72*f, str(d))
        c.setFont('Times-Roman', 24*f)
        c.drawString(xpos[i]+55*f, h-72*f, calendar.day_name[dw])
    y = h-130*f - step*(16+1)
    c.setLineWidth(2*f)
    c.setStrokeColor(navy)
    c.line(xpos[2], y, w-w_margin, y)
    c.setFont('Times-Roman', 45*f)
    c.setFillColor(navy)
    c.drawString(xpos[2], y+8*f, str(week[6][0]))
    c.setFont('Times-Roman', 24*f)
    c.drawString(xpos[2]+55*f, y+8*f, calendar.day_name[week[6][1]])

    # end
    draw_agenda_halfweek_common(c, year, monthnum, weeknum, week, 7,
                                w, h, w_margin)


def agenda_halfweek_view(c, year):
    wholeyear = [cal.monthdays2calendar(year, m+1) for m in range(12)]
    weeknum = 0

    # calc values
    w_margin = 12*f
    w_spacing = 10*f
    w2 = (w-2*w_margin-2*w_spacing) / 3.0
    xpos = [w_margin+i*(w2+w_spacing) for i in range(3)]

    # show week
    skipnext = False
    for monthnum, month in enumerate(wholeyear):
        m1, y1 = m2, y2 = monthnum+1, year
        for week in month:
            if skipnext:
                skipnext = False
                continue
            weeknum += 1
            if weeknum == 1 and week[0][0] == 0: # beginning of year
                nw, m1, y1 = __get_prevweek(year, monthnum+1)
                week = [(week[i][0]+nw[i][0], week[i][1]+nw[i][1]) for i in range(7)]
            else:
                m1, y1 = monthnum+1, year
            if week[6][0] == 0: # end of month
                nw, m2, y2 = __get_nextweek(year, monthnum+1)
                week = [(week[i][0]+nw[i][0], week[i][1]+nw[i][1]) for i in range(7)]
                skipnext = True
            draw_agenda_halfweek_1(c, year, m1, y1, weeknum, monthnum, week,
                                   w, h, w_margin, xpos)
            draw_agenda_halfweek_2(c, year, m2, y2, weeknum, monthnum, week,
                                   w, h, w_margin, xpos, w2)


######################################################################
##### DAY
def draw_day(c, year, month, day, dw):
    if 'i' in cfg.format:
        c.linkRect('Index', 'index', (0, h, w, h-45*f))

    # calc values
    w_margin = 12*f
    weeknum = date(year, month, day).isocalendar()[1]

    # main division lines
    c.setStrokeColor(lightcoral)
    c.setLineWidth(3*f)
    c.line(w_margin, h-45*f, w-w_margin, h-45*f)

    # header
    c.setFillColor(lightcoral)
    c.setFont('Times-Roman', 35*f)
    c.drawString(w_margin, h-35*f, '%s, %d %s %d' % \
                 (calendar.day_name[dw], day, calendar.month_name[month], year))
    c.setFillColor(navy)
    c.setFont('Times-Roman', 24*f)
    c.drawRightString(w-w_margin, h-35*f, 'Week: %d' % weeknum)

    # months
    w2 = w / 7.0
    x0, y0 = w-w_margin-w2, h-70*f
    if month == 1:
        m, y, links = 12, year-1, False
    else:
        m, y, links = month-1, year, True
    nanocal_month(c, y, m, x0, y0, w2, False, 8*f, links)
    nanocal_month(c, year, month, x0, y0-60*f, w2, True, 8*f)
    if month == 12:
        m, y, links = 1, year+1, False
    else:
        m, y, links = month+1, year, True
    nanocal_month(c, y, m, x0, y0-120*f, w2, False, 8*f, links)

    # lines
    c.setLineWidth(1*f)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setFillColor(navy)
    c.setFont('Times-Roman', 10*f)
    step = 20*f
    y0 = h-45*f-1.4*step
    for i in range(10):
        c.line(w_margin, y0-i*step, x0-w_margin, y0-i*step)
    y0 = y0-i*step
    for i in range(26):
        c.line(w_margin, y0-i*step, w-w_margin, y0-i*step)
        if i%2 == 0:
            c.drawString(w_margin, y0-i*step+3*f, str(i/2+8))

    # end
    c.bookmarkPage('agenda_day_%d/%d/%d' % (year, month, day))
    add_pagenumber(c)
    add_copyright(c)
    c.showPage()


def day_view(c, year, add_blank=False):
    for m in xrange(12):
        for d, dw in cal.itermonthdays2(year, m+1):
            if d == 0:
                continue
            draw_day(c, cfg.year, m+1, d, dw)
            if add_blank:
                blank(c)


######################################################################
##### MAIN
class Config(object):
    def __init__ (self):
        self.year = YEAR
        self.output = None
        self.first_week_day = FIRST_WEEK_DAY
        self.size = A4
        self.compression = 1 # enabled
        self.format = DEFAULT_FORMAT
        self.quiet = False
        self.copyright = True


def usage ():
    print __doc__

    
def version():
    print __doc__.split('\n')[0] + ' - version ' + __revision__


def main():
    global cfg, cal

    # parse arguments and options
    cfg = Config()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvw:y:o:s:f:cq',
                                   ['help', 'version', 'first-week-day=',
                                    'year=', 'output=', 'page-size=',
                                    'format=', 'no-compression', 'quiet'])
    except getopt.GetoptError:
        print 'ERROR: Invalid argument\n'
        usage()
        sys.exit(2)
    # options
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(2)
        if o in ('-v', '--version'):
            version()
            sys.exit(2)
        if o in ('-c', '--no-compression'):
            cfg.compression = 0
        if o in ('-w', '--first-week-day'):
            try:
                firstday = int(a)
                if firstday <0 or firstday > 6:
                    raise ValueError
            except ValueError:
                print 'ERROR: first day of week must be a number between 0 ' \
                       '(monday) and 6 (sunday)\n'
                usage()
                sys.exit(2)
            else:
                cfg.first_week_day = firstday
        if o in ('-y', '--year'):
            try:
                cfg.year = int(a)
            except ValueError:
                print 'ERROR: year must a number\n'
                usage()
                sys.exit(2)
        if o in ('-o', '--output'):
            if not a.endswith('.pdf'):
                a += '.pdf'
            cfg.output = a
        if o in ('-s', '--page-size'):
            if a.upper() not in PAGE_SIZES.keys():
                print 'ERROR: not a valid page size\n'
                usage()
                sys.exit(2)
            cfg.size = PAGE_SIZES[a.upper()]
        if o in ('-f', '--format'):
            for e in a:
                if e not in SECTIONS.keys():
                    print 'ERROR: bad format string "%s", unknown section type "%s"\n' % \
                        (a, e)
                    usage()
                    sys.exit(2)
            cfg.format = a
        if o in ('-q', '--quiet'):
            cfg.quiet = True

    # update values
    if not cfg.output:
        cfg.output = OUTPUT_PRE + '%d.pdf' % cfg.year
    cal = calendar.Calendar(cfg.first_week_day)

    # create sections
    c = prepare_canvas(cfg.year)
    if not cfg.quiet:
        print 'Building the agenda for the year %d. File "%s"' % \
            (cfg.year, cfg.output)
    for it in cfg.format:
        if it in SECTIONS.keys():
            if not cfg.quiet:
                print 'Creating section: %s' % SECTIONS[it][0]
            exec(SECTIONS[it][1])
        else:
            print 'Unknown section type: %s, skipping' % it
    c.save()


if __name__ == '__main__':
    main()


######################################################################
