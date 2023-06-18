from flask import render_template, Blueprint, request
import re
import subprocess
import socket
import dns.resolver
import whois
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time


network_module = Blueprint("network_module", __name__)

@network_module.route('/network_result', methods=["POST"])
def network_result():
    class DomainScanner:

        def __init__(self, target_domain):
            self.target_domain = target_domain
            self.ip = socket.gethostbyname(target_domain)
            self._nmap_result = None
            

        def get_ip_info(self):
            """
            IP 정보 가져오기
            """
            try:
                hostname = socket.gethostbyaddr(self.ip)[0]
                return (f"{self.ip}의 호스트 이름: {hostname}")
            except:
                return (f"{self.ip}의 호스트 이름을 찾을 수 없습니다.")

        def get_whois_info(self):
            """
            Whois 정보 가져오기
            """
            domain = self.target_domain.replace("www.", "")
            whois_result = whois.whois(domain)
            return whois_result

        def run_nmap(self):
            """
            Nmap 실행
            """
            command = f"/Nmap/nmap -p 1-1500 --script dns-brute.nse {self.target_domain} "
            result = subprocess.check_output(command, shell=True)

            # IP 주소 추출
            ip_address = re.search(r'Nmap scan report for .* \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)', result.decode('utf-8')).group(1)

            # rDNS 레코드 추출
            rdns_record = re.search(r'rDNS record for .*: (.*)', result.decode('utf-8')).group(1)


            # 포트 정보 추출
            port_info = re.findall(r'\d+\/\w+\s+\w+\s+\w+', result.decode('utf-8'))
            port_numbers = [line.split('/')[0] for line in port_info]

            # DNS 브루트포스 결과의 도메인 및 IP 주소 추출
            dns_brute = re.findall(r'\s+\|\s+(\S+)\s+-\s+([\d:.]+)', result.decode('utf-8'))

            # DNS 브루트포스 결과 |_가 존재하는 마지막 라인 
            dns_brute_last = re.findall(r'\s+\|_\s+(\S+)\s+-\s+([\d:.]+)', result.decode('utf-8'))
            #두 리스트 합치기 
            dns_brute.extend(dns_brute_last)

            return {
                "ip_addresses": ip_address,
                "rdns_records": rdns_record,
                "port_info": port_info,
                "port_numbers": port_numbers,
                "subdomains": dns_brute,
            }


        def get_server_version(self):
            """
            서버 버전 가져오기
            """
            ports = [int(p) for p in self.run_nmap()["port_numbers"]]
            server_info = []
            for port in ports:
                try:
                    response = requests.get("http://" + self.target_domain + ":" + str(port), timeout=1)  # GET 요청 보내기
                    if response:  # 응답 객체가 None이 아닌 경우에만 처리
                        if response.status_code == 200:  # 응답 코드가 200이면(정상 응답)
                            if 'Server' in response.headers:
                                server_version = response.headers["Server"]  # 서버 버전 정보 가져오기
                                server_info.append(server_version.split('/')[0] + '/' + server_version.split('/')[1].split()[0])

                            else:  # 서버 헤더가 없으면
                                soup = BeautifulSoup(response.text, "html.parser")  # BeautifulSoup 객체 생성
                                server_tag = soup.find("meta", attrs={"name": "generator"})  # <meta name="generator" content="...">
                                if server_tag:
                                    server_version = server_tag.get("content")
                                    server_info.append(server_version.split('/')[0] + '/' + server_version.split('/')[1].split()[0])                 
                except Exception as e:
                    #print(f"Error occurred while trying to access {self.target_domain}:{port}: {e}")
                    pass

            if server_info:
                return server_info
            else:
                return None

        def get_cve_info(self, server_info):
            server_info = server_info.replace("/", " ")
            base_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
            cve_data = []

            params = {
                "keyword": server_info,
                "resultsPerPage": 50
            }

            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                for result in data["result"]["CVE_Items"]:
                    cve_id = result["cve"]["CVE_data_meta"]["ID"]
                    description = result["cve"]["description"]["description_data"][0]["value"]
                    if "baseMetricV3" in result["impact"]:
                        cvss_score = result["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
                    else:
                        cvss_score = "N/A"
                    categories = result["cve"]["problemtype"]["problemtype_data"][0]["description"][0]["value"]
                    cve_data.append({"CVE ID": cve_id, "Description": description, "CVSS Score": cvss_score, "Category": categories})
            else:
                print(f"Error: {response.status_code}")

            return cve_data
    # DomainScanner 객체 생성
    domain_scanner = DomainScanner('www.joongsint.com')

    # 네트워크 결과 가져오기
    try:
        ip_info = domain_scanner.get_ip_info()
        print(ip_info)
    except:
        ip_info='ip_info'
        print(ip_info)
    
    #try:
    #    whois_info = domain_scanner.get_whois_info()
    #except:
    #    whois_info='whois_info'
    #    print(whois_info)
    #nmap_result = domain_scanner.run_nmap()
    # try:
    #     nmap_result = domain_scanner.run_nmap()
    # except:
    #     nmap_result='nmap_result'
    #     print(nmap_result)
    
    try:
        server_info = domain_scanner.get_server_version()
    except:
        server_info='server_info'
        print(server_info)
    
    cve_info = []
    for i in range(len(server_info)):
        cve_info.append(domain_scanner.get_cve_info(server_info[i]))


    # HTML 파일에 결과 값 전달
    return render_template('network_result.html', ip_info=ip_info, server_info=server_info, cve_info=cve_info)