# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

urlwidth = 35 # min(60, max(filter(len, URLS)))

import curses
import gocept.httop.checker
import os.path
import time


def float_format(f):
    if f is None:
        return 'n/a  '
    return ('%.2f' % f).rjust(5, '0')

def update_config(checkers):
    try:

        urls = open(os.path.expanduser('~/.httop'))
    except Exception:
        return

    urls = urls.readlines()
    urls = [url[:-1] for url in urls]
    urls = [url for url in urls if not url.startswith('#')]

    # Add new checkers
    for url in urls:
        if url not in [x.url for x in checkers]:
            checker = gocept.httop.checker.URLChecker(url)
            checker.setDaemon(True)
            checker.start()
            checkers.append(checker)
    checkers.sort(key=lambda x:x.url)

    # Remove old checkers
    for checker in checkers:
        if checker.url not in urls:
            checker.running = False
            checkers.remove(checker)

def mainloop(mainwin):
    checkers = []
    while True:
        update_config(checkers)
        mainwin.clear()
        url_head = '%s  %s   %s   %s   %s   %s   %s  %s %s\n' % (
            ' URL'.ljust(urlwidth),
            'Last', 'Min ', 'Max ', 'Avg ', 'Avg5', 'Avg100', 'Code',
            'Errors')
        mainwin.addstr(url_head)
        for checker in checkers:
            url = '%s%s' % ((checker.checking and '*' or ' '), checker.url)
            url_col = url.ljust(urlwidth)[:urlwidth]
            last_col = float_format(checker.last)
            min_col = float_format(checker.min)
            max_col = float_format(checker.max)
            avg_col = float_format(checker.avg)
            avg5_col = float_format(checker.avg5)
            avg100_col = float_format(checker.avg100)
            code_col = str(checker.code).ljust(4)
            info = '%s  %s  %s  %s  %s  %s  %s   %s %s\n' % (
                url_col, last_col, min_col, max_col,
                avg_col, avg5_col, avg100_col, code_col,
                checker.errors)
            if checker.last > 2:
                attributes = curses.A_BOLD
            else:
                attributes = curses.A_NORMAL
            mainwin.addstr(info, attributes)
        mainwin.refresh()
        time.sleep(0.05)

def main():
    screen = curses.initscr()
    curses.start_color()
    try:
        curses.curs_set(0)
    except:
        pass
    curses.noecho()
    curses.cbreak()

    mainwin = curses.newwin(0,0)

    try:
        mainloop(mainwin)
    except:
        curses.nocbreak()
        try:
            curses.curs_set(1)
        except:
            pass
        curses.echo()
        curses.endwin()
        raise
