import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_snap(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.snap'):
            file_dir, file_name = os.path.split(file_found)
            temp_data_list = []
            file_parts = (file_name.replace('.snap', '')).split('_')
            temp_data_list.append(file_parts[0])
            temp_data_list.append(file_parts[1])
            data_list.append(temp_data_list)

    usageentries = len(data_list)
    if usageentries > 0:
        report = ArtifactHtmlReport(f'Snap Packages')
        #check for existing and get next name for report file, so report from another file does not get overwritten
        report_path = os.path.join(report_folder, f'snap_packages.temphtml')
        report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
        report.start_artifact_report(report_folder, os.path.basename(report_path))
        report.add_script()
        data_headers = ('package_name', 'version')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = f'snap_package'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc(f'No snap package data available')
