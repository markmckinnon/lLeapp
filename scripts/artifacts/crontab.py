import os
from crontab import CronTab

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name,get_user_name_from_path_via_position


def get_crontab(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        file_dir = file_found.split(seeker.directory + '\\')[1]
        if file_dir.startswith('etc'):
            username = 'root'
        elif 'docker' in file_dir:
            username = 'docker-diff'
        else:
            username = get_user_name_from_path_via_position(file_found,2)
        data_list = []
        cron = CronTab(tabfile=file_found)
        for job in cron:
            temp_data_list = []
            temp_data_list.append(job.command)
            if job.user == None:
                temp_data_list.append("")
            else:
                temp_data_list.append(job.user)
            temp_data_list.append(job.minute)
            temp_data_list.append(job.hour)
            temp_data_list.append(job.dom)
            temp_data_list.append(job.month)
            temp_data_list.append(job.dow)
            data_list.append(temp_data_list)

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{username} Crontab')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{username}_crontab.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('command', 'user', 'minute', 'hour', 'day_of_month', 'month_of_year', 'day_of_week')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'{username}_crontab'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No {username} crontab data available')
