#!c:\usr\lib\python23\python.exe

from dirstat.Configuration import Configuration
import dirstat

def main() :
    Configuration().set_strvalue('dumper','Ming')
    dirstat.main()

if __name__ == '__main__' :
    main()

