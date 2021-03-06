# -*- coding: utf-8 -*-
#
# LOKI Logger

import sys, re
from colorama import Fore, Back, Style
from colorama import init
import codecs
import datetime
import traceback
from helpers import removeNonAsciiDrop

__version__ = '0.22.0'

# Logger Class -----------------------------------------------------------------
class LokiLogger():

    no_log_file = False
    log_file = "loki.log"
    csv = False
    hostname = "NOTSET"
    alerts = 0
    warnings = 0
    notices = 0
    only_relevant = False
    debug = False
    linesep = "\n"

    def __init__(self, no_log_file, log_file, hostname, csv, only_relevant, debug, platform, caller):
        self.no_log_file = no_log_file
        self.log_file = log_file
        self.hostname = hostname
        self.csv = csv
        self.only_relevant = only_relevant
        self.debug = debug
        self.caller = caller
        if platform == "windows":
            self.linesep = "\r\n"

        # Colorization ----------------------------------------------------
        init()

        # Welcome
        if not self.csv:
            self.print_welcome()

    def log(self, mes_type, message):

        # Remove all non-ASCII characters
        # message = removeNonAsciiDrop(message)
        codecs.register(lambda message: codecs.lookup('utf-8') if message == 'cp65001' else None)

        if not self.debug and mes_type == "DEBUG":
            return

        # Counter
        if mes_type == "ALERT":
            self.alerts += 1
        if mes_type == "WARNING":
            self.warnings += 1
        if mes_type == "NOTICE":
            self.notices += 1

        if self.only_relevant:
            if mes_type not in ('ALERT', 'WARNING'):
                return

        # to stdout
        try:
            self.log_to_stdout(message.encode('ascii', errors='replace'), mes_type)
        except Exception, e:
            print "Cannot print certain characters to command line - see log file for full unicode encoded log line"
            self.log_to_stdout(removeNonAsciiDrop(message), mes_type)

        # to file
        if not self.no_log_file:
            self.log_to_file(message, mes_type)

    def log_to_stdout(self, message, mes_type):

        # Prepare Message
        codecs.register(lambda message: codecs.lookup('utf-8') if message == 'cp65001' else None)
        message = message.encode(sys.stdout.encoding, errors='replace')

        if self.csv:
            print "{0},{1},{2},{3}".format(getSyslogTimestamp(),self.hostname,mes_type,message)

        else:

            try:

                key_color = Fore.WHITE
                base_color = Fore.WHITE+Back.BLACK
                high_color = Fore.WHITE+Back.BLACK

                if mes_type == "NOTICE":
                    base_color = Fore.CYAN+''+Back.BLACK
                    high_color = Fore.BLACK+''+Back.CYAN
                elif mes_type == "INFO":
                    base_color = Fore.GREEN+''+Back.BLACK
                    high_color = Fore.BLACK+''+Back.GREEN
                elif mes_type == "WARNING":
                    base_color = Fore.YELLOW+''+Back.BLACK
                    high_color = Fore.BLACK+''+Back.YELLOW
                elif mes_type == "ALERT":
                    base_color = Fore.RED+''+Back.BLACK
                    high_color = Fore.BLACK+''+Back.RED
                elif mes_type == "DEBUG":
                    base_color = Fore.WHITE+''+Back.BLACK
                    high_color = Fore.BLACK+''+Back.WHITE
                elif mes_type == "ERROR":
                    base_color = Fore.MAGENTA+''+Back.BLACK
                    high_color = Fore.WHITE+''+Back.MAGENTA
                elif mes_type == "RESULT":
                    if "clean" in message.lower():
                        high_color = Fore.BLACK+Back.GREEN
                        base_color = Fore.GREEN+Back.BLACK
                    elif "suspicious" in message.lower():
                        high_color = Fore.BLACK+Back.YELLOW
                        base_color = Fore.YELLOW+Back.BLACK
                    else:
                        high_color = Fore.BLACK+Back.RED
                        base_color = Fore.RED+Back.BLACK

                # Colorize Type Word at the beginning of the line
                type_colorer = re.compile(r'([A-Z]{3,})', re.VERBOSE)
                mes_type = type_colorer.sub(high_color+r'[\1]'+base_color, mes_type)
                # Break Line before REASONS
                linebreaker = re.compile('(MD5:|SHA1:|SHA256:|MATCHES:|FILE:|FIRST_BYTES:|DESCRIPTION:|REASON_[0-9]+)', re.VERBOSE)
                message = linebreaker.sub(r'\n\1', message)
                # Colorize Key Words
                colorer = re.compile('([A-Z_0-9]{2,}:)\s', re.VERBOSE)
                message = colorer.sub(key_color+Style.BRIGHT+r'\1 '+base_color+Style.NORMAL, message)

                # Print to console
                if mes_type == "RESULT":
                    res_message = "\b\b%s %s" % (mes_type, message)
                    print base_color,res_message,Back.BLACK
                    print Fore.WHITE,Style.NORMAL
                else:
                    sys.stdout.write("%s\b\b%s %s%s%s%s\n" % (base_color, mes_type, message, Back.BLACK,Fore.WHITE,Style.NORMAL))

            except Exception, e:
                traceback.print_exc()
                print "Cannot print to cmd line - formatting error"

    def log_to_file(self, message, mes_type):
        try:
            # Write to file
            with codecs.open(self.log_file, "a", encoding='utf-8') as logfile:
                if self.csv:
                    logfile.write(u"{0},{1},{2},{3}{4}".format(getSyslogTimestamp(), self.hostname, mes_type,message, self.linesep))
                else:
                    logfile.write(u"%s %s LOKI: %s: %s%s" % (getSyslogTimestamp(), self.hostname, mes_type.title(), message, self.linesep))
        except Exception, e:
            traceback.print_exc()
            print "Cannot print line to log file {0}".format(self.log_file)

    def print_welcome(self):

        if self.caller == 'main':
            print Back.GREEN + " ".ljust(79) + Back.BLACK + Fore.GREEN

            print "      __   ____  __ ______                            "
            print "     / /  / __ \/ //_/  _/                            "
            print "    / /__/ /_/ / ,< _/ /                              "
            print "   /____/\____/_/|_/___/                              "
            print "      ________  _____  ____                           "
            print "     /  _/ __ \/ ___/ / __/______ ____  ___  ___ ____ "
            print "    _/ // /_/ / /__  _\ \/ __/ _ `/ _ \/ _ \/ -_) __/ "
            print "   /___/\____/\___/ /___/\__/\_,_/_//_/_//_/\__/_/    "

            print Fore.WHITE
            print "   (C) Florian Roth"
            print "   June 2017"
            print "   Version %s" % __version__
            print "  "
            print "   DISCLAIMER - USE AT YOUR OWN RISK"
            print "  "
            print Back.GREEN + " ".ljust(79) + Back.BLACK
            print Fore.WHITE+''+Back.BLACK

        else:
            print "  "
            print Back.GREEN + " ".ljust(79) + Back.BLACK + Fore.GREEN

            print "  "
            print "  LOKI UPGRADER "

            print "  "
            print Back.GREEN + " ".ljust(79) + Back.BLACK
            print Fore.WHITE + '' + Back.BLACK

def getSyslogTimestamp():
    date_obj = datetime.datetime.utcnow()
    date_str = date_obj.strftime("%Y%m%dT%H:%M:%SZ")
    return date_str
