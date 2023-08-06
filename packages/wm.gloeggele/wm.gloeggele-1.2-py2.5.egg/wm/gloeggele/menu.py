import optparse
import urllib
import xml.etree.ElementTree as ET
import datetime

MENU = 'http://www.gloeggele.com/de/tagesmenue.xml'
DATE_FMT = '%d.%m.%Y'


class Menu(object):

    def __init__(self, element):
        self.element = element

    @property
    def text(self):
        quoted = self.element.find('text').text
        if not quoted:
            return None
        return urllib.unquote(quoted).replace('+', ' ')

    @property
    def datetext(self):
        return self.element.find('title').text

    @property
    def date(self):
        try:
            return datetime.datetime.strptime(self.datetext, DATE_FMT).date()
        except (ValueError, TypeError):
            # date of weekbeater is in invalid format -> valueerror
            # datetext is None -> TypeError
            return None


class MenuPlan(object):

    def __init__(self, url):

        filename, headers = urllib.urlretrieve(url)
        self.tree = ET.parse(filename)
        self.menus = self.tree.getroot().getchildren()

    def _getMenuForDate(self, datetimedate):

        searchDate = datetimedate.strftime(DATE_FMT)

        try:
            menu = [entry for entry in self.menus \
                    if entry.find('title').text == searchDate][0]
            #root.findall('*/title[@text="%s"]' % today) # new in 1.3
            return Menu(menu)
        except IndexError:
            return None

    @property
    def allMenus(self):
        """return all menus of this week that have a valid date
        we dont check if the date is really in this week since sometimes
        inconsistent data is put online
        """

        for menu in [Menu(entry) for entry in self.menus]:
            if menu.date:
                yield menu

    @property
    def todaysMenu(self):

        return self._getMenuForDate(datetime.date.today())

    @property
    def weekmenu(self):

        try:
            weekmenu = [entry for entry in self.menus \
                        if entry.get('id') == '6'][0]
            return Menu(weekmenu)
        except IndexError:
            return None


def printMenu(menu):

    print menu.date.strftime('\n%A, %x')
    import textwrap
    print textwrap.fill(menu.text, initial_indent="  ", subsequent_indent="  ")


def printMenuPlan(menuplan):

    for menu in menuplan.allMenus:
        printMenu(menu)


def printWeekMenu(menuplan):
    """if weekmenu can be found: print it
    """

    if menuplan.weekmenu:
        print '\nWeekbeater'
        import textwrap
        print textwrap.fill(menuplan.weekmenu.text,
                            initial_indent="  ",
                            subsequent_indent="  ")


def printTodayMenu(menuplan):

    today = menuplan.todaysMenu
    if not today:
        print "no menu found for today"
    else:
        printMenu(today)


def main():

    parser = optparse.OptionParser(usage="""%prog [options]

%prog efficiently displays the menu-plan online available at gloeggele.com""")

    parser.add_option('-a', '--all', action='store_true',
                      dest='showWeek', default=False,
                      help="show menu for each day of this week")
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

    if options.showWeek:
        printMenuPlan(menuplan)
    else:
        printTodayMenu(menuplan)

    printWeekMenu(menuplan)


if __name__ == "__main__":
    main()
