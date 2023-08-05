#!c:\usr\lib\python24\python.exe

from dirstat.Configuration import Configuration
import dirstat

def main() :
    Configuration().set_strvalue('dumper','SVG')
    dirstat.main()

if __name__ == '__main__' :
    main()

