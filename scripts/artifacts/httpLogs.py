import os
from apachelogs import LogParser, InvalidEntryError

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lleapfuncs import logfunc, tsv, timeline, get_next_unused_name


def get_apache_logs(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        source_file = file_found.replace(seeker.directory, "")
        data_list = []
        ip_connection_bytes_dict = {}
        ip_connection_pages_dict = {}
        request_method_counts = {}
        request_method_bytes = {}
        uri_bytes_dict = {}

        parser = LogParser("%a %h %l %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"")
        with open(file_found, 'r') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    temp_data_list = []
                    entry = parser.parse(line)
                    remote_ip = entry.remote_address
                    timestamp = entry.request_time
                    request = entry.request_line
                    requests = entry.request_line.split(" ")
                    request_method = requests[0]
                    request_uri = requests[1]
                    referer = entry.headers_in['Referer']
                    user_agent = entry.headers_in['User-Agent']
                    status = entry.final_status
                    bytes_out = entry.bytes_out
                    temp_data_list = (timestamp, remote_ip, request, status, bytes_out, referer, user_agent, source_file)
                    data_list.append(temp_data_list)
                    if remote_ip in ip_connection_bytes_dict:
                        ip_connection_bytes_dict[remote_ip] = ip_connection_bytes_dict[remote_ip] + bytes_out
                    else:
                        ip_connection_bytes_dict[remote_ip] = bytes_out
                    if remote_ip in ip_connection_pages_dict:
                        ip_connection_pages_dict[remote_ip] = ip_connection_pages_dict[remote_ip] + 1
                    else:
                        ip_connection_pages_dict[remote_ip] = 1
                    if request_uri in uri_bytes_dict:
                        uri_bytes_dict[request_uri] = uri_bytes_dict[request_uri] + bytes_out
                    else:
                        uri_bytes_dict[request_uri] = bytes_out
                    if request_method in request_method_counts:
                        request_method_counts[request_method] = request_method_counts[request_method] + 1
                    else:
                        request_method_counts[request_method] = 1
                    if request_method in request_method_bytes:
                        request_method_bytes[request_method] = request_method_bytes[request_method] + bytes_out
                    else:
                        request_method_bytes[request_method] = bytes_out
                except InvalidEntryError as e:
                    continue

        usageentries = len(data_list)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_access_log History')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_access_log.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('timestamp', 'remote_ip', 'request', 'status', 'bytes_out', 'referer', 'user_agent','sourcefile')

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'apache_access_log History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'apache_access_log History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No apache_access_log data available')

        usageentries = len(ip_connection_bytes_dict)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_IP_bytes History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_IP_bytes.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('ip_address', 'num_of_bytes', 'sourcefile')

            ip_bytes = []
            for ip_key in ip_connection_bytes_dict.keys():
                ip_bytes.append((ip_key, ip_connection_bytes_dict[ip_key], source_file))

            report.write_artifact_data_table(data_headers, ip_bytes, file_found)
            report.end_artifact_report()

            tsvname = f'apache_IP_bytes History'
            tsv(report_folder, data_headers, ip_bytes, tsvname)

        else:
            logfunc(f'No apache_IP_bytes data available')

        usageentries = len(ip_connection_pages_dict)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_IP_page_accesses History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_IP_page_accesses.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('ip_address', 'num_of_resources_accessed', 'sourcefile')

            ip_page_accesses = []
            for ip_key in ip_connection_pages_dict.keys():
                ip_page_accesses.append((ip_key, ip_connection_pages_dict[ip_key], source_file))

            report.write_artifact_data_table(data_headers, ip_page_accesses, file_found)
            report.end_artifact_report()

            tsvname = f'apache_IP_page_accesses History'
            tsv(report_folder, data_headers, ip_page_accesses, tsvname)

        else:
            logfunc(f'No apache_IP_page_accesses data available')

        usageentries = len(uri_bytes_dict)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_uri_bytes History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_uri_bytes.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('uri', 'num_of_bytes', 'sourcefile')

            uri_bytes = []
            for uri_key in uri_bytes_dict.keys():
                uri_bytes.append((uri_key, uri_bytes_dict[uri_key], source_file))

            report.write_artifact_data_table(data_headers, uri_bytes, file_found)
            report.end_artifact_report()

            tsvname = f'apache_uri_bytes History'
            tsv(report_folder, data_headers, uri_bytes, tsvname)

        else:
            logfunc(f'No apache_uri_bytes data available')

        usageentries = len(request_method_counts)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_request_method_counts History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_request_method_counts.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('request_method', 'num_of_accesses','sourcefile')

            method_count = []
            for method_key in request_method_counts.keys():
                method_count.append((method_key, request_method_counts[method_key], source_file))

            report.write_artifact_data_table(data_headers, method_count, file_found)
            report.end_artifact_report()

            tsvname = f'apache_method_count History'
            tsv(report_folder, data_headers, method_count, tsvname)

        else:
            logfunc(f'No apache_method_count data available')

        usageentries = len(request_method_bytes)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'apache_request_method_bytes History')
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'apache_request_method_bytes.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('request_method', 'num_of_bytes', 'sourcefile')

            method_bytes = []
            for method_key in request_method_bytes.keys():
                method_bytes.append((method_key, request_method_bytes[method_key], source_file))

            report.write_artifact_data_table(data_headers, method_bytes, file_found)
            report.end_artifact_report()

            tsvname = f'apache_method_bytes History'
            tsv(report_folder, data_headers, method_bytes, tsvname)

        else:
            logfunc(f'No apache_method_bytes data available')


__artifacts__ = {
        "apache_logs": (
                "Apache Logs",
                ('**/var/logs/apache2/access.log'),
                get_apache_logs)
}
