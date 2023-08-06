
import site
import os

pth = os.sep.join(site.__file__.split(os.sep)[:-2])+os.sep+"Scripts"

p4d_bat = open(pth+os.sep+"p4d.bat", "w")
p4d_bat.write("@echo off\n")
p4d_bat.write("python %s"%pth + "\\p4d.py %*")

xml2p4d_bat = open(pth+os.sep+"xml2p4d.bat", "w")
xml2p4d_bat.write("@echo off\n")
xml2p4d_bat.write("p4d --xml2p4d %*")


