import os
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, get_next_unused_name, get_user_name_from_home


def get_docker_config(files_found, report_folder, seeker, wrap_text):

    data_list = []
    data_headers = []
    for file_found in files_found:
        file_found = str(file_found)
        temp_data_list = []
        with open(file_found, 'r', encoding='utf-8') as f:
            container_info = json.load(f)
            container_config = container_info.get('Config', None)
            container_state = container_info.get('State', None)
            if container_config != None:
                temp_data_list.append(container_config.get('Image', ''))
            temp_data_list.append(container_info.get('ID', ''))
            image_id = container_info.get('Image', '')
            if ":" in image_id:
                temp_data_list.append(image_id.split(':')[1])
            else:
                temp_data_list.append('')
            temp_data_list.append(container_info.get('OS', ''))
            temp_data_list.append(container_config.get('WorkingDir', ''))
            temp_data_list.append(container_info.get('EntryPoint', ''))
            temp_data_list.append(container_info.get('Created',''))
            if container_state != None:
                temp_data_list.append(container_state.get('StartedAt', ''))
                temp_data_list.append(container_state.get('FinishedAt', ''))
                temp_data_list.append(container_state.get('Running', ''))
                temp_data_list.append(container_state.get('Paused', ''))
            # Mount_id from another file
            temp_data_list.append('')
            #Upper_dir
            temp_data_list.append('')
            temp_data_list.append(container_info.get('LogPath', ''))
            exposed_port_dict = container_config.get('ExposedPorts', None)
            if exposed_port_dict != None:
                exposed_ports = []
                for key in exposed_port_dict.keys():
                    exposed_ports.append(key)
                temp_data_list.append(exposed_ports)
            else:
                temp_data_list.append('')
        temp_data_list.append(file_found)
        data_list.append(temp_data_list)

    usageentries = len(data_list)
    if usageentries > 0:
        report = ArtifactHtmlReport(f'Docker Config')
        #check for existing and get next name for report file, so report from another file does not get overwritten
        report_path = os.path.join(report_folder, f'Docker_Config.temphtml')
        report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
        report.start_artifact_report(report_folder, os.path.basename(report_path))
        report.add_script()
        data_headers = ('image_name', 'container_id', 'image_id', 'os', 'working_dir', 'entry_point', 'created_date', 'start_date', 'finished_date', 'running', 'paused', 'mount_id', 'upper_id', 'log_path', 'exposed_ports', 'sourcefile')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = f'recent_Documents'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc(f'No Docker data available')

__artifacts__ = {
        "docker_config": (
                "Docker",
                ('**/docker\containers\*\config.v2.json'),
                get_docker_config)
}
