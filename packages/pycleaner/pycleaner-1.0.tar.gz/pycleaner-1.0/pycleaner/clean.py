import os
import sys
# TODO: use optparse

def main():
    path = '.'
    if len(sys.argv) > 1:
        path = sys.argv[1]

    confirm = raw_input('Recursively delete .pyc from [ %s ] ? [Y/n]: ' % (path,))
    if confirm.lower() not in ['y', '']:
        print "Aborting"
        sys.exit(0)
    count = 0
    for name, folders, files in os.walk(path):
        for file in files:
            if file.endswith('.pyc'):
                count+=1
                os.remove(os.path.join(name, file))

    print "Deleted %s files" % (count,)

if __name__ == "__main__":
    main()
