import os
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name


def get_apt_history_log(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        data_list = []
        data_installed_programs_list = []
        data_removed_programs_list = []
        with open(file_found, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Start-Date" in line:
                    line_list = line.split(": ")
                    start_date = line_list[1].replace("  ", " ").strip()
                    utc_start_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    start_epoch_time = (utc_start_time - datetime(1970, 1, 1)).total_seconds()

                if "Commandline" in line:
                    line_list = line.split(": ")
                    command_line = line_list[1]
                if "Install" in line:
                    line_list = line.split(": ")
                    history_type = line_list[0]
                    installed_program = line_list[1]
                    installed_programs = installed_program.split("), ")
                    for program in installed_programs:
                        data_installed_programs_list.append((program.split(' (')[0], start_date, start_epoch_time))
                if "Remove" in line:
                    line_list = line.split(": ")
                    history_type = line_list[0]
                    removed_program = line_list[1]
                    removed_programs = removed_program.split("), ")
                    for program in removed_programs:
                        data_removed_programs_list.append((program.split(' (')[0], start_date, start_epoch_time))
                if "End-Date" in line:
                    line_list = line.split(": ")
                    end_date = line_list[1]
                    if "Install" in history_type:
                        data_list.append((start_date, command_line, history_type, installed_program, end_date, start_epoch_time))
                    else:
                        data_list.append((start_date, command_line, history_type, removed_program, end_date, start_epoch_time))

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apt_history_log History')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apt_history_log.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('start_date', 'commandline', 'type', 'programs', 'end_date', 'start_date_epoch')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'apt_history_log History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'auth_log History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No apt_history_log data available')

        usageentries = len(data_installed_programs_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apt_programs_installed_log History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apt_programs_installed_log.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('installed_program', 'date_installed', 'date_installed_epoch')
            report.write_artifact_data_table(data_headers, data_installed_programs_list, file_found)
            report.end_artifact_report()

            tsvname = f'apt_programs_installed_log History'
            tsv(report_folder, data_headers, data_installed_programs_list, tsvname)

            tlactivity = f'apt_programs_installed_log History'
            timeline(report_folder, tlactivity, data_installed_programs_list, data_headers)
        else:
            logfunc(f'No apt_programs_installed data available')

        usageentries = len(data_removed_programs_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apt_programs_removed_log failed logins History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apt_programs_removed_log.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('removed_program', 'date_removed', 'date_removed_epoch')

            report.write_artifact_data_table(data_headers, data_removed_programs_list, file_found)
            report.end_artifact_report()

            tsvname = f'apt_programs_removed_log History'
            tsv(report_folder, data_headers, data_removed_programs_list, tsvname)

            tlactivity = f'apt_programs_removed_log History'
            timeline(report_folder, tlactivity, data_removed_programs_list, data_headers)
        else:
            logfunc(f'No apt_programs_removed_log data available')


__artifacts__ = {
        "apt_history_log": (
                "APT Logs",
                ('**/var/logs/apt/history.log'),
                get_apt_history_log)
}
