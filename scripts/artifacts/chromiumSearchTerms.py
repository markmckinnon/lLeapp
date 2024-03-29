import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, \
    open_sqlite_db_readonly, get_browser_name, get_user_name_from_home

def get_chromeSearchTerms(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History': # skip -journal and other files
            continue
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
            url_id,
            term,
            id,
            url,
            datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        FROM keyword_search_terms, urls
        WHERE url_id = id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Keyword Search Terms - {user_name}')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Keyword Search Terms - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Visit Time','Term','URL', 'username', 'sourcefile')
            data_list = []
            for row in all_rows:
                if wrap_text:
                    data_list.append((row[4], row[1],(textwrap.fill(row[3], width=100)), user_name, file_found))
                else:
                    data_list.append((row[4], row[1], row[3], user_name, file_found))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} keyword search terms'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Keyword Search Terms'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} keyword search terms data available')
        
        db.close()

__artifacts__ = {
        "chromeSearchTerms": (
                "Browser",
                ('**/home/*/.config/google-chrome/default/History*', '**/home/*/.config/google-chrome/Profile*/History*'),
                get_chromeSearchTerms)
}