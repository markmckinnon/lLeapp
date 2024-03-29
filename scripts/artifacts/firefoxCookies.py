import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name, \
    open_sqlite_db_readonly, get_user_name_from_home

def get_firefoxCookies(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'cookies.sqlite': # skip -journal and other files
            continue

        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''SELECT name, value, host, path, expiry, 
                  ((lastAccessed/1000000) - 11644473600) as lastAccessed, 
                  ((creationTime/1000000) - 11644473600) as creationTime,
                   isSecure, isHttpOnly FROM moz_cookies
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'Firefox Cookies - {user_name}')
            report_path = os.path.join(report_folder, f'Firefox Cookies - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('name', 'value', 'host', 'path', 'expiration', 'last_accessed', 'creation_time', 'is_secure', 'is_http_only', 'username', 'sourcefile')
            data_list = []
            for row in all_rows:
                if wrap_text:
                    data_list.append((row[0],row[1],(textwrap.fill(row[2], width=50)),row[3],row[4],row[5],row[6], row[7], row[8], user_name, file_found))
                else:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6], row[7], row[8], user_name, file_found))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Firefox cookies'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Firefox Cookies'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox cookies data available')
        
        db.close()

__artifacts__ = {
        "firefoxCookies": (
                "Browser",
                ('**/home/*/.mozilla/firefox/*.default/cookies.sqlite*'),
                get_firefoxCookies)
}