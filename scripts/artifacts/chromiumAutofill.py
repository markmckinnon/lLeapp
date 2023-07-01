import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name,\
    does_column_exist_in_db, open_sqlite_db_readonly, get_browser_name, get_user_name_from_home

def get_chromeAutofill(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data': # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute(f'''
        select
            datetime(date_created, 'unixepoch'),
            name,
            value,
            datetime(date_last_used, 'unixepoch'),
            count
        from autofill
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Autofill')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Autofill - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Date Created','Field','Value','Date Last Used','Count','username', 'sourcefile')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4], user_name, file_found))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Autofill'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Autofill'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} Autofill data available')
        
        db.close()

__artifacts__ = {
        "chromeAutofill": (
                "Browser",
                ('**/home/*/.config/google-chrome/default/Web Data*', '**/home/*/.config/google-chrome/Profile*/Web Data*'),
                get_chromeAutofill)
}
