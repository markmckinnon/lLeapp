import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name


def get_auth_log(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        data_list = []
        sudo_data_list = []
        failed_data_list = []
        with open(file_found, 'r') as f:
            lines = f.readlines()
            for line in lines:
                temp_data_list = []
                sudo_temp_data_list = []
                failed_temp_data_list = []
                timestamp = line[:15]
                temp_data_list.append(timestamp)
                newLine = line[15:]
                lineList = newLine.split(': ')
                host_process_list = lineList[0].split(" ")
                host = ""
                process = ""
                xtype = ""
                message = ""
                if len(host_process_list) == 3:
                    host = host_process_list[1]
                    process = host_process_list[2]
                elif len(host_process_list) == 2:
                    host = host_process_list[0]
                    host = host_process_list[1]
                else:
                    host = host_process_list[0]
                if len(lineList) == 2:
                    message = lineList[1].strip()
                elif len(lineList) == 3:
                    xtype = lineList[1]
                    message = lineList[2].strip()
                elif len(lineList) == 4:
                    xtype = lineList[1]
                    message = lineList[3].strip()
                else:
                    print("This was not expected")

                temp_data_list.append(host)
                temp_data_list.append(process)
                temp_data_list.append(xtype)
                temp_data_list.append(message)
                data_list.append(temp_data_list)

                if 'sudo' in process:
                    if 'pam' not in xtype:
                        sudo_temp_data_list.append(timestamp)
                        sudo_temp_data_list.append(host)
                        sudo_temp_data_list.append(xtype)
                        for sudo_data in message.split(' ; '):
                            sudo_temp_data_list.append(sudo_data)
                        sudo_data_list.append(sudo_temp_data_list)

                if 'FAILED' in line:
                    failed_temp_data_list.append(timestamp)
                    failed_temp_data_list.append(host)
                    failed_temp_data_list.append(process)
                    failed_temp_data_list.append(message)
                    failed_data_list.append(failed_temp_data_list)

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'auth_log History')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'auth_log.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('timestamp', 'host', 'process', 'type', 'message')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'auth_log History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'auth_log History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No auth_log data available')

        usageentries = len(sudo_data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'auth_log sudo History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'auth_log_sudo.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('timestamp', 'host', 'user', 'terminal', 'print_working_directory', 'run_as', 'command')

            report.write_artifact_data_table(data_headers, sudo_data_list, file_found)
            report.end_artifact_report()

            tsvname = f'auth_log sudo History'
            tsv(report_folder, data_headers, sudo_data_list, tsvname)

            tlactivity = f'auth_log sudo History'
            timeline(report_folder, tlactivity, sudo_data_list, data_headers)
        else:
            logfunc(f'No auth_log sudo data available')

        usageentries = len(failed_data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'auth_log failed logins History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'auth_log_failed_logins.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('timestamp', 'host', 'process', 'message')

            report.write_artifact_data_table(data_headers, failed_data_list, file_found)
            report.end_artifact_report()

            tsvname = f'auth_log Failed Logins History'
            tsv(report_folder, data_headers, failed_data_list, tsvname)

            tlactivity = f'auth_log Failed Logins History'
            timeline(report_folder, tlactivity, failed_data_list, data_headers)
        else:
            logfunc(f'No auth_log FAILED data available')
