import optparse
import urllib
import elementtree.ElementTree as ET
import datetime

MENU = 'http://www.gloeggele.com/de/tagesmenue.xml'

class Menu(object):

    def __init__(self, element):
        self.element = element

    @property
    def text(self):
        quoted = self.element.find('text').text
        return urllib.unquote(quoted).replace('+', ' ')

    @property
    def date(self):
        return self.element.find('title').text


class MenuPlan(object):

    def __init__(self, url):
        filename, headers = urllib.urlretrieve(url)
        self.tree = ET.parse(filename)
        self.menus = self.tree.getroot().getchildren()

    def _getMenuForDate(self, datetimedate):
        searchDate = datetimedate.strftime('%d.%m.%Y')

        try:
            menu = [entry for entry in self.menus if entry.find('title').text == searchDate][0]
            #root.findall('*/title[@text="%s"]' % today) # new in 1.3
            return Menu(menu)
        except IndexError:
            return None


    @property
    def todaysMenu(self):
        return self._getMenuForDate(datetime.date.today())

    @property
    def weekmenu(self):

        try:
            weekmenu = [entry for entry in self.menus if entry.get('id') == '6'][0]
            return Menu(weekmenu)
        except IndexError:
            return None



def main():
    parser = optparse.OptionParser(usage = """%prog""")
    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return

    try:
        menuplan = MenuPlan(MENU)
    except IOError, e:
        print "menuplan could not be loaded from %s" % MENU
        print e
        return 1

    today = menuplan.todaysMenu
    weekmenu = menuplan.weekmenu


    if not today:
        print "no menu found for today"
    else:
        print ("="*10 + " menu for %(date)s " + "="*10 + "\n%(menu)s\n")   % {'date': today.date, 'menu': today.text}

    if weekmenu:
        print ("="*10 + " weekbeater " + "="*10 + "\n%(menu)s") % {'menu': weekmenu.text}


if __name__ == "__main__": main()