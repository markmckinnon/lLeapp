import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name, get_user_name_from_home

def get_trash_name(path):
    new_path = os.path.normpath(path)
    path_list = new_path.split(os.sep)
    new_path_list = []
    for part_name in path_list:
        if part_name == 'info':
            break
        new_path_list.append(part_name)
    return os.sep.join(new_path_list)

def get_trash(files_found, report_folder, seeker, wrap_text):

    data_list = []
    owner = None
    for file_found in files_found:
        file_found = str(file_found)
        if owner != None and owner != get_user_name_from_home(file_found):
            report = ArtifactHtmlReport(f'Trash')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'Trash.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('file_name', 'owner', 'original_path', 'delete_date')

            report.write_artifact_data_table(data_headers, data_list, os.path.join(trash_path,'files'))
            report.end_artifact_report()

            tsvname = f'Trash'
            tsv(report_folder, data_headers, data_list, tsvname)

            data_list = []

        owner = get_user_name_from_home(file_found)
        path = ""
        deletion_date = ""
        with open(file_found, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if '[Trash Info]' in line:
                    continue
                if 'Path' in line:
                    file_path = line.split("=")[1]
                if 'DeletionDate' in line:
                    deletion_date = line.split("=")[1]
            data_list.append((os.path.basename(file_path).replace("%20", " "), owner, file_path, deletion_date))
        trash_path = get_trash_name(file_found)

    usageentries = len(data_list)
    if usageentries > 0:
        report = ArtifactHtmlReport(f'Trash')
        #check for existing and get next name for report file, so report from another file does not get overwritten
        report_path = os.path.join(report_folder, f'Trash.temphtml')
        report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
        report.start_artifact_report(report_folder, os.path.basename(report_path))
        report.add_script()
        data_headers = ('file_name', 'owner', 'original_path', 'delete_date')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Trash'
        tsv(report_folder, data_headers, data_list, tsvname)
            
    else:
        logfunc(f'No trash data available')
