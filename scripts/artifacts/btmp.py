import os
import utmp

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name


def get_btmp(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        data_list = []
        with open(file_found, 'rb') as f:
            buf = f.read()
            for entry in utmp.read(buf):
                temp_data_list = []
                # print(entry.time, entry.type, entry)
                temp_data_list.append(entry.user)
                if entry.line == '~':
                    temp_data_list.append("")
                else:
                    temp_data_list.append(entry.line)
                temp_data_list.append(entry.host)
                temp_data_list.append(entry.time)
                temp_data_list.append(entry.sec)
                data_list.append(temp_data_list)

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'btmp History')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'btmp.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('user', 'terminal', 'host', 'timestamp', 'epoch_timestamp')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'btmp History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'btmp History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No btmp data available')
