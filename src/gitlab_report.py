# Library imports and error subpression
import math
import time
import gitlab
import datetime
import urllib3
import threading

# Suppress SSL warnings as we are a master user
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Object to hold info on projects + issues.
class ProjectHolder:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.list = list()
    
    def add_issue(self, issue):
        self.list.append(issue)
    
    def compare_holder(self, enemy_holder):
        return self.title==enemy_holder.title

# Object to hold info on milestones + projects
class MilestoneHolder:
    def __init__(self, title, start_end_date):
        self.title = title
        self.list = list()
        self.start_end_date = start_end_date
    
    def add_issue(self, project, issue):
        curr_holder = ProjectHolder(project.name, project.web_url)
        curr_holder.add_issue(issue)
        unique = True
        for project in self.list:
            if project.compare_holder(curr_holder):
                unique = False
                project.add_issue(issue)
                break
        if unique:
            self.list.append(curr_holder)

    def compare_holder(self, enemy_holder):
        return self.title==enemy_holder.title
    
# Read configuration settings from txt
def read_config(config_file_path):
    with open(config_file_path, 'r', encoding='utf-8') as conf:
        config_lines = conf.readlines()
    config = {
        'verbose': config_lines[0][14:-1] == "1",
        'months_back': int(config_lines[1][19:-1]),
        'gitlab_url': config_lines[2][13:-1],
        'private_token': config_lines[3][16:]
    }
    return config

# Authenticate with GitLab
def authenticate_gitlab(gitlab_url, private_token):
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token, ssl_verify=False)
    try:
        gl.auth()
        print("Authentication successful")
        return gl
    except gitlab.exceptions.GitlabAuthenticationError:
        print("Authentication failed. Check your token and URL.")
        exit(1)

# Compose GitLab report file
def write_report(file, milestone_list, verbose, months_back, current_date_time):
    print("\nWriting Report...")

    issue_count = 0
    closed_count = 0
    open_count = 0

    current_date_time = datetime.datetime.now()

    num_milestones = len(milestone_list)
    mCount = 1
    pCount = 1
    iCount = 1

    for milestone in milestone_list:
        file.write("------------------------------------\n")
        file.write(f"Milestone: {milestone.title}\n")
        file.write(f"{milestone.start_end_date}\n")
        file.write("------------------------------------\n")

        num_projects = len(milestone.list)

        for project in milestone.list:
            file.write(f"\tProject Name: {project.title}\n")
            if verbose:
                file.write(f"\tProject URL: {project.url}\n\n")
            file.write("\t------------------------------------\n")

            num_issues = len(project.list)

            for issue in project.list:
                print(f"\rMilestone {mCount}/{num_milestones}, Project {pCount}/{num_projects}, Issue {iCount}/{num_issues}", end='')

                in_date_range = True
                if issue.state == 'closed':
                    issue_close_date_time = datetime.datetime.strptime(issue.closed_at[:10], "%Y-%m-%d")
                    in_date_range = (current_date_time - issue_close_date_time).days // 30 <= months_back
                if in_date_range:
                    issue_count += 1
                    file.write(f"\t\tIssue Title: {issue.title}\n")
                    file.write(f"\t\tState: {issue.state}\n")
                    if verbose:
                        file.write(f"\t\tCreated At: {issue.created_at}\n")
                        file.write(f"\t\tUpdated At: {issue.updated_at}\n")
                    if issue.state == 'closed': 
                        closed_count += 1
                        if verbose:
                            file.write(f"\t\tClosed At: {issue.closed_at}\n")
                    else:
                        open_count += 1
                    file.write("\t\tLabel:\n")
                    for label in issue.labels:
                        file.write(f"\t\t\t{label}\n")
                    file.write("\n\t\tDescription:\n")
                    file.write(f"\t\t{issue.description}\n")
                    file.write("\n\t\t------------------------------------\n")

                iCount += 1

            pCount += 1
            iCount = 1

        mCount += 1
        pCount = 1

    print("\nReport Generated!")

    file.write(f"\nTotal Issues: {issue_count}\nClosed Issues: {closed_count}\nOpen Issues: {open_count}\n")

def waiting(stop):
    flag = stop()
    while(not flag):
        for i in range(3):
            print(".", end='')
            time.sleep(0.5)
        for i in range(3):
            print("\b", end='')
            time.sleep(0.5)
        flag = stop()
    print("...")

# Main method
def main():
    config_file_path = 'configuration.txt'
    text_file_path = 'gitlab_issues_report.txt'
    
    config = read_config(config_file_path)
    gl = authenticate_gitlab(config['gitlab_url'], config['private_token'])

    print("Grabbing projects list from Gitlab API: ", end='')
    stopThread = False
    thread = threading.Thread(target=waiting, args=(lambda : stopThread, ))
    thread.start()
    projects = gl.projects.list(all=True)
    stopThread = True
    thread.join()

    milestone_list = list()

    current_date_time = datetime.datetime.now()
    
    with open(text_file_path, 'w', encoding='utf-8') as file:
        file.write("GitLab Issues Report\n")
        file.write(f"Verbose Mode: {config['verbose']}\n")
        file.write(f"Closed issues still displayed after {config['months_back']} months\n")
        file.write("====================\n\n")

        print("Grabbing issues for each project: ", end='')
        project_count = 1
        num_projects = len(projects)
        EPSILON = 0.000001
        num_projects_digits = math.floor(math.log(num_projects, 10) + EPSILON) + 1

        for project in projects:
            print(f"{project_count}/{num_projects}", end='')
            issues = project.issues.list(all=True)
            if issues:
                for issue in issues:
                    if issue.milestone:
                        milestone_title = issue.milestone['title']
                        milestone_start = issue.milestone.get('start_date', 'No start date')
                        milestone_end = issue.milestone.get('due_date', 'No due date')
                        milestone_start_end = f"Start date: {milestone_start}, End date: {milestone_end}"
                        if issue.milestone['state'] != 'active':
                            milestone_close_date_time = datetime.datetime.strptime(issue.milestone['updated_at'][:10], "%Y-%m-%d")
                            in_date_range = (current_date_time - milestone_close_date_time).days // 30 <= config['months_back']
                        else:
                            in_date_range = True
                    else:
                        milestone_title = "none"
                        milestone_start_end = "Issues without a milestone"
                        in_date_range = True
                    if in_date_range:
                        curr_holder = MilestoneHolder(milestone_title, milestone_start_end)
                        curr_holder.add_issue(project, issue)
                        unique = True
                        for holder in milestone_list:
                            if holder.compare_holder(curr_holder):
                                unique = False
                                holder.add_issue(project, issue)
                                break
                        if unique:
                            milestone_list.append(curr_holder)

            num_backspaces = 2 + math.floor(math.log(project_count, 10) + EPSILON) + num_projects_digits
            if project_count < num_projects:
                for backspace in range(num_backspaces):
                    print("\b", end='')
                project_count += 1

        write_report(file, milestone_list, config['verbose'], config['months_back'], current_date_time)

if __name__ == "__main__":
    main()
