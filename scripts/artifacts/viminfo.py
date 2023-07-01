import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name, get_user_name_from_home


def get_viminfo(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        file_dir = file_found.split(seeker.directory + '\\')[1]
        data_list = []
        edited_files = {}
        data_headers_file_mark = []
        data_headers_jumplist = []
        data_headers_history_of_marks = []
        owner = get_user_name_from_home(file_found)
        with open(file_found, 'r') as f:
            lines = f.readlines()
            file_type = ''
            for line in lines:
                if '# File marks:' in line:
                    file_type = 'marks'
                    continue
                elif '# Jumplist (newest first):' in line:
                    file_type = 'jumplist'
                    continue
                elif '# History of marks within files' in line:
                    file_type = 'history'
                    continue
                if 'marks' in file_type or 'jumplist' in file_type:
                    file_marks = line.split("  ")
                    if len(file_marks) == 4:
                        if file_marks[3] not in edited_files:
                            edited_files[file_marks[3].strip()] = ''
                elif 'history' in file_type:
                    if ">" in line:
                        if line[2:] not in edited_files:
                            edited_files[line[2:].strip()] = ''

        for key in edited_files.keys():
            data_list.append((owner, key, file_found))

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'vim_edited_files')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'vim_edited_files.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('owner', 'document_name', 'sourcefile')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'vim_edited_files'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No vim edited files data available')

__artifacts__ = {
        "viminfo": (
                "Recent Documents",
                ('**/home/*/.viminfo'),
                get_viminfo)
}