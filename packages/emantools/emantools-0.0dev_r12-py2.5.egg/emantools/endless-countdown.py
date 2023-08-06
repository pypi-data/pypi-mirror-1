#!/usr/bin/env python
#endless-countdown.py

from time import sleep
from daemon import Daemon
import countdown

class Countdown(Daemon):
    interval = 5

    def __init__(self):
        self.main()

    def run_script(self, num, *args):
        t = countdown.countdown(*args)
        fp = open('countdown%s.log' % num, 'w')
        fp.write(t + '\n')
        fp.close()

    def run(self):
        date = (2008, 10, 22, 4, 30)
        self.run_script(0, *date)
        sleep(3)
        self.run_script(1, *date)
        sleep(3)
        self.run_script(2, *date)
        sleep(3)


if __name__ == '__main__':
    Countdown()

