#
#    Copyright (C) 2004-2005  Bryan Lawrence and James Tauber
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


__provider__      = "CalendarProvider"
__contributions__ = {}    

from bel.parts.web_resource import PagePart


import os, os.path, time



class CalendarProvider:

    def __init__(self, resource_manager, lfs, config):
        
        self.config              = config
        self.calendar_key        = config.get("blogcalendar", "calendar_key")
        self.monthly_archive_key = config.get("blogcalendar", "monthly_archive_key")
        
        
    def get(self, resource_id, request, main_resource):

        if resource_id == self.calendar_key:
            return BlogCalendarPart(resource_id, request, self.config)
        elif resource_id == self.monthly_archive_key:
            return MonthlyArchivePart(resource_id, request, self.config)
        else:
            return None

    
    def post(self, resource_id, request, main_resource):
    
        return None



class BlogCalendarPart(PagePart):

    def __init__(self, key, request, config):
        """
        this is called by the menu but we get the context from the
        request itself.
        """

        PagePart.__init__(self, key)
        
        self.relative_path = request.relative_path
        self.site_url      = config.get("blog", "site_url")
        self.blog_path     = config.get("blog", "blog_path")
        self.lfs_root      = config.get("DEFAULT", "lfs_root")

        path = self.relative_path

        # five cases:
        #    blog:  - serve up latest month 
        #    blog/year - serve up Jan
        #    blog/year/month - serve up year/month
        #    blog/year/month/day - serve up year/month
        #    anything else - serve up latest month
        # where of course blog is the config blog prefix ...

        bl = len(self.blog_path)
        if path[0:bl] != self.blog_path or path[bl:bl+1] != "/":
            # serve up latest month
            y, m = time.gmtime()[0:2]
        else:
            lookingfor = path[bl+1:]
            slash = lookingfor.find("/")
            try:
                if slash == -1:
                    y = int(lookingfor)
                    m = 1
                else:
                    y = int(lookingfor[0:4])
                    m = int(lookingfor[5:7])
            except ValueError:
                y, m = time.gmtime()[0:2]

        year, last, this, next = self.title_links(y, m)

        self.html = HtmlCalendar(y, m, self.day_links(y, m), (last, next), this, year)

                 
    def day_links(self,y,m):

        # Jump directly down to the month ...
        links = {}
        tail = "".join([self.blog_path, "/", str(y), "/", "%2.2i" % m])
        monthdir = self.lfs_root + tail
        base = self.site_url + tail
        if os.path.isdir(monthdir):
            blogs = os.listdir(monthdir)
            for blog in blogs:
                if blog[0:1] != ".":
                    links[int(blog)] = base + "/" + blog
        return links

            
    def title_links(self,y,m):

        def yeartitle(y):
            return "".join([self.site_url, self.blog_path, "/", str(y)])

        def increment(y, m, i):
            mm = m + i
            yy = y
            if mm > 12:
                mm, yy = mm % 12, y + mm / 12
            elif mm < 1:
                mm, yy = 12 + mm, y - 1
            return yy, mm
            
        plus = increment(y, m, 1)
        minus = increment(y, m, -1)
        year = yeartitle(y)
        this = "%s%s%2.2i" % (year, "/", m)
        next = "%s%s%2.2i" % (yeartitle(plus[0]), "/", plus[1])
        last = "%s%s%2.2i" % (yeartitle(minus[0]), "/", minus[1])
        return year, last, this, next             



month_names = ["January ", "February ", "March ", "April ", "May ", "June ",
               "July ", "August ", "September ", "October ", "November ", "December "]



class MonthlyArchivePart(PagePart):

    def __init__(self, key, request, config):

        PagePart.__init__(self, key)

        site_url  = config.get("blog", "site_url")
        blog_path = config.get("blog", "blog_path")
        lfs_root  = config.get("DEFAULT", "lfs_root")

        html = ""

        blog_dir = lfs_root + blog_path
        if os.path.isdir(blog_dir):
            years = os.listdir(blog_dir)
            
            years.sort()
            years.reverse()

            for year in years:
                if year == ".svn":
                    continue
                
                year_dir = lfs_root + blog_path + "/" + year
                if os.path.isdir(year_dir):
                    months = os.listdir(year_dir)
            
                    months.sort()
                    months.reverse()
                    
                    for month in months:
                        if month == ".svn":
                            continue
                    
                        link = site_url + blog_path + "/" + year + "/" + month
                        html += '<p><a href="%s">%s %s</a></p>' % (link, month_names[int(month) - 1], year)
                    
        self.html = html

         
         
def HtmlCalendar(year, month, links={}, arrows=None, monthlink=None, yearlink=None):
    """
    Produces an html table representation of the month. If the links
    argument is passed then it should consist of a set of links keyed by day
    of the month. If the arrows argument is passed, then it should consist of
    a two member tuple which has the links to the previous and next month.
    If the monthlink argument is passed, then it should be used as a link
    from the month title, if the yearlink argument is passed it can be used as
    the yearlink title.
    """
   
    months = ["January ", "February ", "March ", "April ", "May ", "June ",
              "July ", "August ", "September ", "October ", "November ", "December "]

    # Ok, I know I should be able to find someone elses code to do this,
    # but it'll take longer to find it than write it
    
    import calendar

    def makelink(target, link):
        return "".join(['<a href="',target,'">',link,"</a>"])

    def monthtitle(m, link, short=0):
        title = months[m - 1]
        if short:
            title = title[0:3]
        if link is None:
            return title
        else:
            return makelink(link, title)

    tr=("<tr>","</tr>")
    td=("""<td align="center">""","</td>")
   
    if yearlink == None:
        yeartitle = str(year)
    else:
        yeartitle = makelink(yearlink, str(year))

    if arrows == None:
        template = "".join(["""<table><tr><td align="center" colspan="7">""",
                          monthtitle(month, monthlink), yeartitle, "</td></tr>"])
    else:
        template = "".join(["<table><tr>", td[0], makelink(arrows[0], "&lt;&lt;"), 
                          td[1], """<td align="center" colspan="5">""",
                          monthtitle(month, monthlink, short=1), " ",
                          yeartitle, "</td>", td[0],
                          makelink(arrows[1], "&gt;&gt;"), td[1], tr[1]])
    
    template += tr[0]
    for day in ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"):
        template += "".join([td[0], day, td[1]])

    template += tr[1]
    matrix = calendar.monthcalendar(year, month)
    for week in matrix:
        row = tr[0]
        for day in week:
            if day != 0:
                if day not in links.keys():
                    row += "".join([td[0], str(day), td[1]])
                else:
                    row += "".join([td[0], makelink(links[day], str(day)), td[1]])
            else:
                row += "".join(td)
        row += tr[1]
        template += row
    template += "</table>"
    
    return template
