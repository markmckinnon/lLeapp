import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_osinfo(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        file_dir = file_found.split(seeker.directory + '\\')[1]
        if file_dir.startswith('usr') or file_dir.startswith('etc'):
            data_list = []
            data_headers = []
            with open(file_found, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    os_info_list = line.split("=")
                    temp_data_list = [os_info_list[0], os_info_list[1].replace('"', "")]
                    data_list.append(temp_data_list)

            usageentries = len(data_list)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'OS Info')
                #check for existing and get next name for report file, so report from another file does not get overwritten
                report_path = os.path.join(report_folder, f'osinfo.temphtml')
                report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
                report.start_artifact_report(report_folder, os.path.basename(report_path))
                report.add_script()
                data_headers = ('name', 'value')

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'osname'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc(f'No osname data available')

__artifacts__ = {
        "osInfo": (
                "OS Info",
                ('**/usr/lib/os-release', '**/etc/os-release'),
                get_osinfo)
}