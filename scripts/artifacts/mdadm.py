import os
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name


def get_mdadm(files_found, report_folder, seeker, wrap_text):

    data_list = []
    data_headers = ['array', 'device_name', 'sourcefile']
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                temp_data_list = []
                if 'ARRAY ' in line:
                    array_list = line.split()
                    # Pop the first 2 entries off as they should alwasy be the same
                    temp_data_list.append(array_list.pop(0))
                    temp_data_list.append(array_list.pop(0))
                    for item in array_list:
                        item_list = item.split("=")
                        if item_list[0] in data_headers:
                            col_num = data_headers.index(item_list[0])
                            temp_data_list.insert(col_num, item_list[1])
                        else:
                            data_headers.append(item_list[0])
                            col_num = data_headers.index(item_list[0])
                            temp_data_list.insert(col_num, item_list[1])
                temp_data_list.append(file_found)
                data_list.append(temp_data_list)

    usageentries = len(data_list)
    if usageentries > 0:
        report = ArtifactHtmlReport(f'mdadm arrays')
        #check for existing and get next name for report file, so report from another file does not get overwritten
        report_path = os.path.join(report_folder, f'mdadm_arrays.temphtml')
        report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
        report.start_artifact_report(report_folder, os.path.basename(report_path))
        report.add_script()

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = f'mdadm_arrays'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc(f'No mdadm arrays data available')

__artifacts__ = {
        "mdadm": (
                "Raids",
                ('**/etc/mdadm/mdadm.conf'),
                get_mdadm)
}