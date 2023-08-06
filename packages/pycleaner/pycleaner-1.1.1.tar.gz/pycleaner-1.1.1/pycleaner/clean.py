import os
import sys
import shutil
# TODO: use optparse

def main():
    path = '.'
    if '-svn' in sys.argv:
        svnrm = []
        print "Recursively Removing .svn folders"
        for name, folders, files in os.walk('.'):
            for folder in folders:
                if folder == '.svn':
                    svnrm.append(os.path.join(name, folder))
        for item in svnrm:
            shutil.rmtree(item)
        print "removed", len(svnrm), "items"
    confirm = raw_input('Recursively delete *.pyc and *~ from [ %s ] ? [Y/n]: ' % (path,))
    if confirm.lower() not in ['y', '']:
        print "Aborting"
        sys.exit(0)
    count = 0
    for name, folders, files in os.walk(path):
        for file in files:
            if file.endswith('.pyc') or file.endswith('~'):
                count+=1
                os.remove(os.path.join(name, file))

    print "Deleted %s files" % (count,)

if __name__ == "__main__":
    main()
