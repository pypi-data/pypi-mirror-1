
import sys
import string
if __name__ == '__main__':
    fid = open(sys.argv[1], "r")
    strAll = ""
    while 1:
        line = fid.readline()
        if not line :
            break
        strAll = strAll + line
    print strAll
    if string.find(strAll, '\r') >2:
        strAll = strAll.replace('\r','\n')
        print strAll
    fid.close()

    fid2 = open(sys.argv[1], "w")
    fid2.write(strAll)
    fid2.close()