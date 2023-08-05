from EasyExtend.eeconsole import EEConsole
import sys

__transit_version__ = "0.1"

class TransitConsole(EEConsole):

    def at_start(self):
        if hasattr(self.fiber, "prompt"):
            sys.ps1 = self.prompt = self.fiber.prompt
        else:
            sys.ps1 = self.prompt = ">>> "
        sys.ps2 = "."*(len(self.prompt)-1)+" "
        print
        print "_________________________________________________________________________________________"
        print
        print "               ____     "
        print "                /  _  _      _  ' _/"
        print "               (  /  (/ /) _)  /  / "
        print
        print " Transit v%s on Python %-66s"%(__transit_version__,sys.version)
        print
        print " Fiber documentation: www.fiber-space.de/EasyExtend/doc/transit/transit.html"
        print "_________________________________________________________________________________________"
        print

    def at_exit(self):
        "reset default prompt"
        sys.ps1 = ">>> "
        sys.ps2 = "... "
        print "_________________________________________________________________________________________"
        print

