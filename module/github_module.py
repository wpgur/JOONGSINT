from flask import Blueprint, render_template, request
import requests, base64, time, re, os
from config import github_access_token
from datetime import datetime

github_module = Blueprint("github_module", __name__)

@github_module.route("/github_result", methods=["POST"])
def github_result():

    class GithubAnalyzer:
        def __init__(self, access_token, username, keywords):
            self.access_token = access_token
            self.username = username
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/vnd.github.v3+json"
            }
            self.keywords = keywords
            self.van_list = ["integrity", "sha512"]
            self.result_folder = os.path.join(os.getcwd(), self.username)
            self.ip_regex = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            self.phone_regex = r'\b(?:\d{2,3}-)?\d{3,4}-\d{4}\b'
            self.email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            self.sum_content = []
            self.start_time = datetime.today().strftime("%Y%m%d%H%M%S")  
            self.log_path = ''
            if request.cookies.get('folder') is not None :
                self.log_path = './crawling_log/' + request.cookies.get('folder').encode('latin-1').decode('utf-8') + '/'
            else:
                self.log_path = './crawling_log/none/'
            self.log_path += username

            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)
                
        def get_user_repositories(self):
            url = f"https://api.github.com/users/{self.username}/repos"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                repositories = response.json()
                return repositories
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)
                return None

        def search_repository_contents(self, repository_name, path=""):
            url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                return contents
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)
                return None

        def search_file_contents(self, repository_name, file_path):
            url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                content = response.json()
                if "content" in content:
                    return {"content": content["content"], "file_path": file_path}
                else:
                    print("File content not found.")
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)

        def traverse_directory(self, repository_name, path=""):
            contents = self.search_repository_contents(repository_name, path)
            repo_dic = {}
            repo_list = []

            if contents is not None:
                for content in contents:
                    if content["type"] == "file":
                        file_path = content["path"]
                        file_result = self.search_file_contents(repository_name, file_path)

                        if file_result is not None:
                            try:
                                file_contents = file_result["content"]
                                file_path = file_result["file_path"]
                                # Check if the file is a PDF
                                if file_path.endswith(".pdf"):
                                    # Create a directory for the repository if it does not exist
                                    repo_dir = os.path.join(self.result_folder, repository_name)
                                    if not os.path.exists(repo_dir):
                                        os.makedirs(repo_dir)
                                    # Get the download URL of the PDF
                                    pdf_url = f"https://github.com/{self.username}/{repository_name}/blob/master/{file_path}?raw=true"
                                    # Save the download URL into the file 'pdf_link.txt'
                                    with open(os.path.join(repo_dir, "pdf_link.txt"), "a") as pdf_link_file:
                                        pdf_link_file.write(f"{file_path}: {pdf_url}\n")
                                else:
                                    decoded_content = base64.b64decode(file_contents).decode("utf-8")
                                    lines = decoded_content.splitlines()
                                    for line in lines:
                                        dicts = {}
                                        for keyword in self.keywords:
                                            if re.search(keyword, line, re.IGNORECASE) and not any(van in line for van in self.van_list):
                                                result_file = os.path.join(self.result_folder, f"{repository_name}.txt")
                                                with open(result_file, "a", encoding="utf-8") as f:
                                                    f.write(f"repo: {repository_name}\n")
                                                    f.write(f"path: {file_path}\n")
                                                    f.write(f"content: {line}\n\n")
                                                dicts['path'] = file_path
                                                dicts['content'] = line
                                                repo_list.append(dicts)

                                        if re.search(self.ip_regex, line) or re.search(self.phone_regex, line) or re.search(self.email_regex, line):
                                            result_file = os.path.join(self.result_folder, f"{repository_name}.txt")
                                            with open(result_file, "a", encoding="utf-8") as f:
                                                f.write(f"repo: {repository_name}\n")
                                                f.write(f"path: {file_path}\n")
                                                f.write(f"content: {line}\n\n")
                                            dicts['path'] = file_path
                                            dicts['content'] = line
                                            repo_list.append(dicts)

                                        
                            except UnicodeDecodeError:
                                continue

                        elif content["type"] == "dir":
                            dir_path = content["path"]
                            self.traverse_directory(repository_name, dir_path)       
            if len(repo_list) == 0:
                pass
            else:
                repo_dic[repository_name] = repo_list
                self.sum_content.append(repo_dic)
            return self.sum_content

        def analyze(self):
            repositories = self.get_user_repositories()
            if repositories is not None:
                sorted_repositories = sorted(repositories, key=lambda x: x["stargazers_count"], reverse=True)
                
                repository_names = []
                
                for repo in sorted_repositories:
                    repository_names.append(repo["name"])
                    print(repo["name"])

                if not os.path.exists(self.result_folder):
                    os.makedirs(self.result_folder)

                for repo_name in repository_names:
                    result = self.traverse_directory(repo_name)
                    time.sleep(1)
            return result


    github_username = request.cookies.get('NAME')

    filter_keyword = ''
    log_path = './crawling_log/' + request.cookies.get('NAME').encode('latin-1').decode('utf-8')+'/'
    if request.cookies.get('keyword') not in [None, ''] :
        filter_keyword = request.cookies.get('keyword').encode('latin-1').decode('utf-8')
        keyword = [filter_keyword.strip() for filter_keyword in filter_keyword.split(",")]
    else :
        filter_keyword = 'None'
    analyzer = GithubAnalyzer(github_access_token, github_username, keyword)
    result = analyzer.analyze()
    print(result)
    return render_template("github_result.html", filter_keyword=filter_keyword, folder_path=log_path, result=result)