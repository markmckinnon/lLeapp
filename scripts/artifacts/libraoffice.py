import os
import xmltodict

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name, get_user_name_from_home


def get_libraOfficeRecentFiles(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        data_list = []
        data_headers = []
        owner = get_user_name_from_home(file_found)
        with open(file_found, 'r') as f:
            xml_content = f.read()
            my_ordered_dict = xmltodict.parse(xml_content)
            items = my_ordered_dict['oor:items']['item']
            for item in items:
                if 'org.openoffice.Office.Histories:HistoryInfo' in item['@oor:path']:
                    node = item['node']
                    temp_data_list = []
                    temp_data_list.append(owner)
                    temp_data_list.append(node['@oor:name'])
                    temp_data_list.append(file_found)
                    data_list.append(temp_data_list)

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'Recent Documents')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'Recent_Documents - {owner}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('owner', 'document_name', 'sourcefile')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'recent_Documents'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc(f'No libraOffice recent Document data available')

__artifacts__ = {
        "libraoffice": (
                "Recent Documents",
                ('**/home/*/.config/libreoffice/4/user/registrymodifications.xcu'),
                get_libraOfficeRecentFiles)
}
