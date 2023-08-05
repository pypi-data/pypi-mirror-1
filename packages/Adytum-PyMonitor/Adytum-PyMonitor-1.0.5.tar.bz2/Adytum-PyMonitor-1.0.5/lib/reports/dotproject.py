'''
When run from the command line, you need to pass a user id, a start date,
and an optional end date.
'''

import sys
import MySQLdb

DEBUG = 0
DBUSER = 'dotproject'
DBPASS = 'dotproject'
DB = 'dotproject'

SQL_PART_ENDDATE_NOW = 'AND task_log_date <= CURDATE()'
SQL_PART_ENDDATE = "AND task_log_date <= '%s'"
SQL_USERS = '''SELECT user_id, user_username FROM users;'''
SQL_PROJECTS = '''SELECT project_id, project_name, TRIM(SUBSTRING(project_short_name, 1, 6)) FROM projects;'''
SQL_TASK_PROJECTS = '''SELECT task_id, task_project FROM tasks;'''
SQL_ALL_CLIENTS_ALL_PROJECTS = '''SELECT task_log_task, TRIM(SUBSTRING(task_log_name, 1, 12)),
task_log_date, task_log_hours, TRIM(SUBSTRING(task_log_description, 1, 47))
FROM task_log
WHERE (task_log_creator = %s AND task_log_date >= '%s' %s AND task_log_hours > 0)
ORDER BY task_log_date; '''
SQL_ALL_CLIENTS_ALL_PROJECTS_SUM = '''SELECT SUM(task_log_hours) FROM task_log 
WHERE (task_log_creator = %s AND task_log_date >= '%s' %s);
'''

class DotProjectReport:

    def __init__(self, userid=None, begindate=None, enddate=None, payrate=None):
        # initialize basic vars
        self.userid = userid
        self.begindate = begindate
        self.rate = int(payrate)
        self.enddate = enddate
        self.usermap = {}
        self.projectmap = {}
        self.taskprojectmap = {}
        self.userdroplist = []
        self.projectdroplist = []
        self.taskprojectdroplist = []

        # initialize query vars
        self.enddate_query = ''

        # setup database connection
        self.db = MySQLdb.connect(user=DBUSER, passwd=DBPASS, db=DB)
        self.cursor = self.db.cursor()

    def setEndDate(self):
        if not self.enddate:
            self.enddate_query = SQL_PART_ENDDATE_NOW
        else:
            self.enddate_query = SQL_PART_ENDDATE % self.enddate

    def getUserMap(self):
        self.cursor.execute(SQL_USERS)
        for row in self.cursor.fetchall():
            user_id, user_username = row
            self.usermap[user_id] = user_username
        return self.usermap

    def getUserDropList(self):
        '''
        This method is useful for dropdowns, in that it preserves
        the order returned by the SQL query, but also has a
        value/friendly-name pairing.
        '''
        if not self.usermap:
            self.getUserMap()
        for user_id, user_username in self.usermap.items():
            self.userdroplist.append({user_id: user_username})
        return self.userdroplist
            
    def getProjectMap(self):
        self.cursor.execute(SQL_PROJECTS)
        for row in self.cursor.fetchall():
            id, long_name, short_name = row
            self.projectmap[id] = (short_name, long_name)
        return self.projectmap

    def getProjectDropList(self):
        '''
        This method is useful for dropdowns, in that it preserves
        the order returned by the SQL query, but also has a
        value/friendly-name pairing.
        '''
        if not self.projectmap:
            self.getProjectMap()
        for project_id, name_tuple in self.projectmap.items():
            long_name = name_tuple[1]
            self.projectdroplist.append({project_id: long_name})
        return self.projectdroplist

    def getTaskProjectMap(self):
        self.cursor.execute(SQL_TASK_PROJECTS)
        for row in self.cursor.fetchall():
            task_id, proj_id = row
            self.taskprojectmap[task_id] = proj_id
        return self.taskprojectmap

    def getTaskProjectDropList(self):
        '''
        This method is useful for dropdowns, in that it preserves
        the order returned by the SQL query, but also has a
        value/friendly-name pairing.
        '''
        if not self.taskprojectmap:
            self.getTaskProjectMap()
        for task_id, proj_id in self.getTaskProjectMap.items():
            self.taskprojectdroplist.append({task_id: proj_id})
        return self.taskprojectdroplist

    def getAllClientsAllProjects(self):
        if not self.projectmap:
            self.getProjectMap()
        if not self.taskprojectmap:
            self.getTaskProjectMap()
        projs_map = self.projectmap
        tasks_map = self.taskprojectmap

        distinct_projs = {}
        output = "Date \t\tProj \tTask \t\tHours \tDescription\n"
        output += "==== \t\t==== \t==== \t\t===== \t===========\n"
        sql = SQL_ALL_CLIENTS_ALL_PROJECTS % (self.userid, self.begindate, self.enddate_query)
        #print sql
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            id, name, date, time, desc = row
            proj = projs_map[tasks_map[id]][0]
            distinct_projs.setdefault(proj, 0)
            distinct_projs[proj] = distinct_projs[proj] + time
            date = date.strftime('%Y-%m-%d')
            output += "%s \t%s \t%s \t%s \t%s\n" % (date, proj, name, time, desc)
        
        output += "\nProject Summaries:\n"
        output += "Proj   \tHours \tCost\n"
        output += "====   \t===== \t====\n"

        for proj, hours in distinct_projs.items():
	    output += "%s\t%.2f \t%.2f\n" % (proj, hours, hours * self.rate)

        self.cursor.execute(SQL_ALL_CLIENTS_ALL_PROJECTS_SUM % (self.userid, self.begindate, self.enddate_query))

        total = self.cursor.fetchone()[0] or 0.0
        output += '\nTotal hours: %.2f\n' % total
        output += 'Total amount: %.2f\n\n' % (total * self.rate)

        return output


if __name__ == '__main__':

    # setup the args
    args = sys.argv
    #print args
    if DEBUG:
            print args
    userid, payrate, begindate = args[1:4]
    try:
        enddate = args[4]
    except:
        enddate = ''
    if DEBUG:
        print userid, begindate, enddate

    # with the args setup, now instantiate report
    report = DotProjectReport(userid=userid, payrate=payrate, begindate=begindate)
    report.setEndDate()
    print report.getAllClientsAllProjects()
