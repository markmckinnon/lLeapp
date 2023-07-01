import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, \
    get_user_name_from_home, get_next_unused_name


def get_firefox(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'places.sqlite': # skip -journal and other files
            continue

        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        column_exists = does_column_exist_in_db(db, 'moz_places', 'visit_count_local')
        if column_exists:
            cursor.execute('''
            SELECT  
            datetime("visit_date"/1000, 'unixepoch') as visit_date, 
            moz_places.url, 
            moz_places.title, 
            moz_places.visit_count_local, 
            moz_historyvisits.from_visit, 
            moz_places.hidden, 
            moz_places.typed, 
            moz_historyvisits.visit_type 
            FROM moz_places, moz_historyvisits 
            WHERE moz_places.id = moz_historyvisits.place_id    
            ''')
        else:
            cursor.execute('''
            SELECT  
            datetime("visit_date"/1000, 'unixepoch') as visit_date, 
            moz_places.url, 
            moz_places.title, 
            moz_historyvisits.from_visit, 
            moz_places.hidden, 
            moz_places.typed, 
            moz_historyvisits.visit_type 
            FROM moz_places, moz_historyvisits 
            WHERE moz_places.id = moz_historyvisits.place_id    
            ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'Firefox History - {user_name}')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'Firefox History - {user_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()

            if column_exists:
                data_headers = ('Visit Date', 'URL', 'Title', 'Visit Count', 'From Visit', 'Hidden', 'Typed', 'Visit Type', 'username', 'sourcefile')
            else:
                data_headers = ('Visit Date', 'URL', 'Title', 'From Visit', 'Hidden', 'Typed', 'Visit Type', 'username', 'sourcefile')

            data_list = []
            for row in all_rows:
                if column_exists:
                    if wrap_text:
                        data_list.append((row[0], (textwrap.fill(row[1], width=100)), row[2], row[3], row[4], row[5], row[6], row[7], user_name, file_found))
                    else:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], user_name, file_found))
                else:
                    if wrap_text:
                        data_list.append((row[0], (textwrap.fill(row[1], width=100)), row[2], row[3], row[4], row[5], row[6], user_name, file_found))
                    else:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], user_name, file_found))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Firefox History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Firefox History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox history data available')
        
        db.close()

__artifacts__ = {
        "firefox": (
                "Browser",
                ('**/home/*/.mozilla/firefox/*.default/places.sqlite*'),
                get_firefox)
}
