import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, \
    open_sqlite_db_readonly, get_browser_name, get_user_name_from_home

def get_chromeOmnibox(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Shortcuts'):
            continue # Skip all other files
            
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??
        
        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(last_access_time/ 1000000 + (strftime('%s', '1601-01-01')), "unixepoch"),
        text,
        fill_into_edit,
        url,
        contents,
        description,
        keyword,
        number_of_hits
        from omni_box_shortcuts
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Omnibox - {user_name}')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Omnibox - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Access Timestamp','Text','Fill Into Edit','URL','Contents','Description','Keyword','Number of Hits','username','sourcefile')
            data_list = []
            for row in all_rows:
                if wrap_text:
                    data_list.append((row[0],row[1], row[2],(textwrap.fill(row[3], width=100)),row[4], (textwrap.fill(row[5], width=100)), row[6], row[7], user_name, file_found))
                else:
                    data_list.append((row[0],row[1],row[2],row[3],row[4], row[5], row[6], row[7], user_name, file_found))
            
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Omnibox'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Omnibox'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            logfunc(f'{browser_name} Omnibox data parsed.')
        else:
            logfunc(f'No {browser_name} Omnibox data available')
        
        db.close()

__artifacts__ = {
        "chromeOmnibox": (
                "Browser",
                ('**/.config/google-chrome/Default/Shortcuts*', '**/.config/google-chrome/Profile*/Shortcuts*'),
                get_chromeOmnibox)
}