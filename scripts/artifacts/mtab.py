import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_mtab(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        source_file = file_found.replace(seeker.directory, "")

        try:
            file_dir = file_found.split(seeker.directory + '\\')[1]
        except:
            file_dir = file_found.split(seeker.directory)[1]

        if file_dir.startswith('etc'):
            data_list = []
            with open(file_found, 'r') as f:
                lines = f.readlines()
                file_type = ''
                for line in lines:
                    mtab_list = line.split()
                    if len(mtab_list) == 6:
                        data_list.append((mtab_list[0], mtab_list[1], mtab_list[2], mtab_list[3], mtab_list[4], mtab_list[5], source_file))

            usageentries = len(data_list)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'mounted Devices')
                #check for existing and get next name for report file, so report from another file does not get overwritten
                report_path = os.path.join(report_folder, f'mountedDevices.temphtml')
                report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
                report.start_artifact_report(report_folder, os.path.basename(report_path))
                report.add_script()
                data_headers = ('device_name', 'mount_point', 'filesystem_type', 'mounting_options', 'mount_freq', 'mnt_passno', 'sourcefile')

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'mounted_devices'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc(f'No mounted devices data available')

__artifacts__ = {
        "mtab": (
                "Devices",
                ('**/etc/mtab'),
                get_mtab)
}