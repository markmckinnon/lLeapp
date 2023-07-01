import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, usergen, get_user_name_from_home

def get_chromeSync(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('chromesync.data_store'):
            continue # Skip all other files
        
        user_name = get_user_name_from_home(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
                select idx_origin, idx_signon_realm, idx_username from password_index;
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'Chrome Synced Users - {user_name}')
            report.start_artifact_report(report_folder, 'Chrome Synced Users - {user_name}')
            html_report = report.get_report_file_path()
            report.add_script()
            data_headers = ('url origin', 'url realm', 'username', 'user_name', 'sourcefile')
            data_list = []
            data_list_usernames = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2], user_name, file_found))
                data_list_usernames.append((row[2], row[2], 'ChronmeSync', html_report, ''))
    
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Chrome Synced Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Chrome Synced Users'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            usergen(report_folder, data_list_usernames)
            
        else:
            logfunc('No Chrome Synced Users data available')
        
        db.close()
        
__artifacts__ = {
        "chromeSync": (
                "Browser",
                ('**/home/*/.config/google-chrome/default/chromesync.data_store*', '**/home/*/.config/google-chrome/Profile*/chromesync.data_store*'),
                get_chromeSync)
}