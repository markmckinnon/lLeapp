import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_shadow(files_found, report_folder, seeker, wrap_text):

    passwd_id_value = {'1': 'MD5', '2a': 'Blowfish', '2y': 'Blowfish', '5': 'SHA-256', '6': 'SHA-512'}

    for file_found in files_found:
        file_found = str(file_found)
        data_list = []
        with open(file_found, 'r') as f:
            lines = f.readlines()
            for line in lines:
                temp_data_list = []
                line_data = line.split(":")
                temp_data_list.append(line_data[0])
                if len(line_data[1]) < 2:
                    temp_data_list.append('')
                    temp_data_list.append('')
                    temp_data_list.append('')
                else:
                    password_data = line_data[1].split('$')
                    temp_data_list.append(passwd_id_value[password_data[1]])
                    temp_data_list.append(password_data[2])
                    temp_data_list.append(password_data[3])
                temp_data_list.append(line_data[2])
                temp_data_list.append(line_data[3])
                temp_data_list.append(line_data[4])
                temp_data_list.append(line_data[5])
                temp_data_list.append(line_data[6])
                temp_data_list.append(line_data[7])

                data_list.append(temp_data_list)

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'shadow')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'shadow.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('username', 'passwd_algorithm', 'passwd_salt', 'passwd_hashed', 'last_changed_epoch', 'minimum_passwd_change', 'maximum_passwd_change', 'warn', 'inactive', 'expiration_date_epoch')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'shadow'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc(f'No shadow data available')
