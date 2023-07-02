from flask import Blueprint, render_template, request
from bs4 import BeautifulSoup
import time, re, os
from urllib.parse import urljoin
from urllib.parse import unquote
from datetime import datetime
import os
import ast

report_module = Blueprint("report_module", __name__)

@report_module.route("/report_result", methods=["POST"])
def report_result():
    class Report:
        def __init__(self):
            self.start_time = datetime.today().strftime("%Y%m%d%H%M%S")  
            self.log_path = ''
            if request.cookies.get('folder') is not None :
                self.log_path = './crawling_log/' + request.cookies.get('folder').encode('latin-1').decode('utf-8') + '/'
            else:
                self.log_path = './crawling_log/none/'


        def extract_dict_names(self, directory):
            dict_names = []
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                url_path = filename.replace('-',':').replace('_','/')
                value = {}
                for data_path in os.listdir(f'{file_path}/'):
                    print(f'{file_path}/{data_path}')
                    with open(f'{file_path}/{data_path}', 'r') as file:
                        data = file.read()
                        data_list = ast.literal_eval(data)
                    dict_names.append(data_list)
            #print(dict_names)
            return dict_names
    
    report = Report()
    current_directory = os.getcwd()
    print(f"현재 경로: {report.log_path}")
    result = report.extract_dict_names(report.log_path)


    print(result)
    return render_template("report_result.html", result=result)