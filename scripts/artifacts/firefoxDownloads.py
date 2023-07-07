import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name,\
    open_sqlite_db_readonly, get_user_name_from_home, get_next_unused_name

def get_firefoxDownloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        source_file = file_found.replace(seeker.directory, "")
        if not os.path.basename(file_found) == 'mozac_downloads_database': # skip -journal and other files
            continue

        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT url, file_name, destination_directory, 
                   ((created_at/1000000) - 11644473600) as created_at,
                   content_length, content_type
              FROM downloads
              ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'Firefox Downloads - {user_name}')
            report_path = os.path.join(report_folder, f'Firefox Downloads - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('url', 'file_name', 'destination_directory', 'created_at', 'content_length', 'content_type', 'username','sourcefile')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5], user_name, source_file))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Firefox Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Firefox Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox download data available')
        
        db.close()

__artifacts__ = {
        "firefoxDownloads": (
                "Browser",
                ('**/home/*/.mozilla/firefox/*.default/places.sqlite*'),
                get_firefoxDownloads)
}
