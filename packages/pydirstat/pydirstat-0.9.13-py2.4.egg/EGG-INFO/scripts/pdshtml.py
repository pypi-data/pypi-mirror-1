#!C:\usr\lib\Python24\python.exe

from dirstat.Configuration import Configuration
import dirstat

def main() :
    Configuration().set_strvalue('dumper','HTML')
    dirstat.main()

if __name__ == '__main__' :
    main()

