

# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.chrome import get_chrome
from scripts.artifacts.chromeDownloads import get_chromeDownloads
from scripts.artifacts.chromeCookies import get_chromeCookies
from scripts.artifacts.chromeAutofill import get_chromeAutofill
from scripts.artifacts.chromeLoginData import get_chromeLoginData
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks
from scripts.artifacts.chromeOmnibox import get_chromeOmnibox
from scripts.artifacts.chromeSearchTerms import get_chromeSearchTerms
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.chromeWebsearch import get_chromeWebsearch
from scripts.artifacts.chromeNetworkActionPredictor import get_chromeNetworkActionPredictor
from scripts.artifacts.firefox import get_firefox
from scripts.artifacts.firefoxDownloads import get_firefoxDownloads
from scripts.artifacts.firefoxCookies import get_firefoxCookies
from scripts.artifacts.wtmp import get_wtmp
from scripts.artifacts.btmp import get_btmp
from scripts.artifacts.authLog import get_auth_log
from scripts.artifacts.apacheLogs import get_apache_logs
from scripts.artifacts.aptHistory import get_apt_history_log
from scripts.artifacts.timezone import get_timezone

from scripts.lleapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex_term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

# These are external databases that are created during the run of lLeapp that we want to add into
# after everything has been processed.  The file it looks for is used as a place holder to make the logic
# work, this file should always be present in a ChromeOs system
to_search_external_dbs = {
    'crossArtifactUserids': ('Cross Artifacts', '**/mount/user/.bash_profile'),
    'crossArtifactTimeline': ('Cross Artifacts', '**/mount/user/.bash_profile'),
}

# These are all the artifacts that need to be processed from a ChromeOs
tosearch_lLeapp = {
# Browsers
    'chrome':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeDownloads':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeCookies':('Browser', ('**/mount/user/Cookies*',  '**/chronos/LockScreenAppsProfile/Cookies*', '**/chronos/Default/Cookies*', '**/com.brave.browser/app_chrome/Default/Cookies*', '**/com.opera.browser/app_opera/Cookies*')),
    'chromeLoginData':('Browser', ('**/mount/user/Login Data*', '**/chronos/LockScreenAppsProfile/Login Data*', '**/chronos/Default/Login Data*', '**/com.brave.browser/app_chrome/Default/Login Data*', '**/com.opera.browser/app_opera/Login Data*')),
    'chromeAutofill':('Browser', ('**/mount/user/Web Data*', '**/chronos/LockScreenAppsProfile/Web Data*', '**/chronos/Default/Web Data*', '**/com.brave.browser/app_chrome/Default/Web Data*')),
    'chromeSearchTerms':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeWebsearch':('Browser', ('**/mount/user/History*', '**/chronos/LockScreenAppsProfile/History*', '**/chronos/Default/History*', '**/com.brave.browser/app_chrome/Default/History*', '**/com.opera.browser/app_opera/History*')),
    'chromeTopSites':('Browser', ('**/mount/user/Top Sites*', '**/chronos/LockScreenAppsProfile/Top Sites*', '**/chronos/Default/Top Sites*', '**/com.brave.browser/app_chrome/Default/Top Sites*', '**/com.opera.browser/app_opera/Top Sites*')),
    'chromeNetworkActionPredictor':('Browser', ('*/mount/user/Network Action Predictor*','*/chronos/LockScreenAppsProfile/Network Action Predictor*', '*/chronos/Default/Network Action Predicator*', '**/com.brave.browser/app_chrome/Default/Network Action Predicator*')),
    'chromeOmnibox':('Browser', ('*/mount/user/Shortcuts*','*/chronos/LockScreenAppsProfile/Shortcuts*', '*/chronos/Default/Shortcuts*', '**/com.brave.browser/app_chrome/Default/Shortcuts*')),
    'customDict':('User Settings', '*/mount/user/Custom Dictionary.txt'),
    'firefox':('Browser', '**/org.mozilla.firefox/files/places.sqlite*'),
    'firefoxDownloads':('Browser', '**/org.mozilla.firefox/files/places.sqlite*'),
    'firefoxCookies':('Browser', '**/org.mozilla.firefox/databases/mozac_downloads_database*'),
# Log files
    'wtmp':('Logs', '**/var/logs/wtmp'),
    'btmp': ('Logs', '**/var/logs/btmp'),
    'auth_log': ('Logs', '**/var/logs/auth.log'),
    'apache_logs':('Apache Logs', '**/var/logs/apache2/access.log'),
    'apt_history_log':('APT Logs', '**/var/logs/apt/history.log'),
# Misc Files
    'timezone': ('Timezone', '**/etc/timezone'),
}

# This is the order the artifacts must be processed.
tosearch = dict(tosearch_lLeapp)
tosearch.update(to_search_external_dbs)

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base, output_type):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
            
            wrap_text: whether the text data will be wrapped or not using textwrap.  Useful for tools that want to parse the data.
    '''
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker, output_type)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    logfunc('{} [{}] artifact completed'.format(artifact_name, artifact_func))
    