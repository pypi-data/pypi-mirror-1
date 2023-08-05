import sets
from nodecheck import CheckDir, CheckFile, NotificationServer
from nodecheck import NOTIFY_CHANGE_ALL

def callback(old_data, new_data):
    stat_types = ['bytes', 'atime', 'ctime', 'mtime', 'owner', 'mode', 'contents'] 
    dir_action = ''
    print "There has been a change!"
    for stat in stat_types:
        if old_data[stat] != new_data[stat]:
            printChanges(new_data['path'], stat, old_data[stat], new_data[stat])
            if stat == 'contents':
                old_len = len(old_data[stat])
                new_len = len(new_data[stat])
                # make sets for easy calcs
                old = sets.Set(old_data[stat])
                new = sets.Set(new_data[stat])
                # check which files have been deleted
                if old_len > new_len:
                    files = list(old.difference(new))
                    dir_action = 'removed'
                # check which files have been added
                if old_len < new_len:
                    files = list(new.difference(old))
                    dir_action = 'added'
                print "The following files were %s:" % dir_action
                print files
                
def printChanges(file_name, stat_type, old_stat, new_stat):
        print "File: %s" % file_name
        print "Type: %s" % stat_type
        print "Old Value: %s" % old_stat
        print "New Value: %s" % new_stat




check1 = CheckDir('/tmp')
check2 = CheckFile('/tmp/aaaa.test')

checks = [check1, check2]
flags = [ NOTIFY_CHANGE_ALL ]

ns = NotificationServer(checks, flags, callback)

while True:

    ns.run()
