import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_fstab(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        file_dir = file_found.split(seeker.directory + '\\')[1]
        if file_dir.startswith('etc'):
            data_list = []
            with open(file_found, 'r') as f:
                lines = f.readlines()
                file_type = ''
                for line in lines:
                    if line.startswith('#'):
                        pass
                    else:
                        fstab_list = line.split()
                        if len(fstab_list) == 6:
                            data_list.append((fstab_list[0], fstab_list[1], fstab_list[2], fstab_list[3], fstab_list[4], fstab_list[5]))

            usageentries = len(data_list)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'file system table')
                #check for existing and get next name for report file, so report from another file does not get overwritten
                report_path = os.path.join(report_folder, f'fstab.temphtml')
                report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
                report.start_artifact_report(report_folder, os.path.basename(report_path))
                report.add_script()
                data_headers = ('device_name', 'mount_point', 'filesystem_type', 'mounting_options', 'mount_freq', 'mnt_passno')

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = f'file_system_table'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc(f'No file system table data available')

__artifacts__ = {
        "fstab": (
                "Devices",
                ('**/etc/fstab'),
                get_fstab)
}

