#!/usr/bin/python
import requests, json, csv, io, argparse, sys, os, fileinput, re
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser(description='When run without arguments, this script will generate a list of hosts from the Datadog Inventory')
parser.add_argument('--agentreport', help='generate report of hosts without DD agent installed and email Ops', action='store_true')
args = parser.parse_args()

if len(sys.argv) > 1: # Has arguments
        assert sys.argv[1] in ['--agentreport'], 'Argument should be either --agentreport or None: ' + sys.argv[1]

''' Lets cleanup old files '''
for filex in "all_hosts_from_dd.json", "all_hosts_from_dd_parsed.json", "HOST_INFO_ALL.csv", "HOST_INFO_ALL.json", "DATADOG_REPORT.csv", "HOSTS_WITHOUT_AGENT.json":
	if os.path.exists(filex):
        	os.remove(filex)

#api_key = ''
#application_key = ''

#url = "https://app.datadoghq.com/reports/v2/overview?api_key="+api_key+"&application_key="+application_key+"&metrics=avg%3Asystem.cpu.idle%2Cavg%3Aaws.ec2.cpuutilization%2Cavg%3Avsphere.cpu.usage%2Cavg%3Aazure.vm.processor_total_pct_user_time%2Cavg%3Asystem.cpu.iowait%2Cavg%3Asystem.load.norm.15&with_apps=true&with_sources=true&with_aliases=true&with_meta=true&with_mute_status=true&with_tags=true"
url = "https://datadoghq.com/reports/v2/overview?api_key="+api_key+"&application_key="+application_key+"&window=1w&metrics=avg%3Aaws.ec2.cpuutilization%2Cavg%3Aazure.vm.percentage_cpu%2Cavg%3Agcp.gce.instance.cpu.utilization%2Cavg%3Asystem.cpu.idle%2Cavg%3Asystem.cpu.iowait%2Cavg%3Asystem.load.norm.15%2Cavg%3Avsphere.cpu.usage&with_apps=true&with_sources=true&with_aliases=true&with_meta=true&with_mute_status=true&with_tags=true"
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
r = requests.get(url,headers=headers)

print "status:", r.status_code

def write_host_info_to_file(data):
        host_agent = get_host_info(data)
        if len(sys.argv) > 1: # Has arguments
		#print "Number of arguments: ", len(sys.argv)
                if sys.argv[1] == '--agentreport':
                        print "Test some other function call"
                        with io.open("HOSTS_WITHOUT_AGENT.json",'w', encoding='utf-8') as fb:
                                fb.write(json.dumps(host_agent, indent=2, ensure_ascii=False))
                        print "Saved EC2 Instances report to: HOST_WITHOUT_AGENT.json"
                        convert_to_csv('HOSTS_WITHOUT_AGENT.json')
                        #cmd = "mail -a DATADOG_REPORT.csv -s \"Report: Hosts without Datadog Agent Installed\" user@mail.com  </dev/null"
			cmd = "mutt  -s \"Report: Hosts without Datadog Agent Installed\" -e \"set content_type=text/html\" -a DATADOG_REPORT.csv --  user@mail.com < msg-body.html"
                        os.system(cmd)

                else:
                        assert action in ['--agentreport'], 'Argument should be either --agentreport or None: ' + action
        else:
                with io.open("HOST_INFO_ALL.json",'w', encoding='utf-8') as fc:
                        fc.write(json.dumps(host_agent, indent=2, ensure_ascii=False))
                print "Saved EC2 Instances report to: HOST_INFO_ALL.json"
                convert_to_csv('HOST_INFO_ALL.json')


def get_host_info(data):
	aws_hosts_without_agent_count = 0
	aws_hosts_count = 0
        host_agent = []
        for hosts in data["rows"]:
		if "aws" in hosts["apps"] and "elb" not in hosts["apps"] and ".elb." not in hosts["host_name"]:
                                        aws_hosts_count = aws_hosts_count + 1
                if sys.argv[1] == '--agentreport':
                        if "aws" in hosts["apps"] and "agent" not in hosts["apps"] and "elb" not in hosts["apps"] and ".elb." not in hosts["host_name"]:
                                host_agent.append({"host_name": hosts["host_name"],"aws_name": hosts.get("aws_name"),"display_name": hosts.get("display_name"), "aws_id": hosts.get("aws_id"), "availability-zone": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("availability-zone"),"application_id": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("applicationid"),"aws_account": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("aws_account"),"autoscaling_group": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("autoscaling_group"),"bu": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("bu"),"created_by": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("createdby"),"env": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("env")
,"environment": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("environment"),"iam_profile": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("iam_profile"),"image": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("image"),"instance_type": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("instance-type"),"organization": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("organization"),"region": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("region"),"resourcedesc": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("resourcedesc"),"status": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("status")})
				aws_hosts_without_agent_count = aws_hosts_without_agent_count + 1
                else:
                        if "aws" in hosts["apps"] and "elb" not in hosts["apps"] and ".elb." not in hosts["host_name"]:
                                host_agent.append({"host_name": hosts["host_name"],"aws_name": hosts.get("aws_name"),"display_name": hosts.get("display_name"), "aws_id": hosts.get("aws_id"), "availability-zone": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("availability-zone"),"application_id": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("applicationid"),"aws_account": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("aws_account"),"autoscaling_group": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("autoscaling_group"),"bu": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("bu"),"created_by": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("createdby"),"env": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("env")
,"environment": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("environment"),"iam_profile": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("iam_profile"),"image": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("image"),"instance_type": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("instance-type"),"organization": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("organization"),"region": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("region"),"resourcedesc": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("resourcedesc"),"status": hosts.get("tags_by_source",{}).get("Amazon Web Services",{}).get("status")})
	print "AWS EC2 hosts count: ", aws_hosts_count
	print "AWS EC2 hosts without DD agent: ", aws_hosts_without_agent_count
	''' Begin new logic added '''
 	generate_html(aws_hosts_count,aws_hosts_without_agent_count)	
	''' End new logic '''
        return host_agent

def convert_to_csv(file_obj):
        with open(file_obj, 'r+') as json_file:
                dat = json.load(json_file)


        f = csv.writer(open("DATADOG_REPORT.csv", "wb+"))
        f.writerow(["display_name", "host_name", "aws_account", "region", "availability-zone", "aws_name", "environment", "env", "bu", "organization", "application_id", "instance_type", "image", "created_by", "autoscaling_group", "resourcedesc", "aws_id", "iam_profile", "status"])

        for x in dat:
                f.writerow([x["display_name"],x["host_name"],x["aws_account"],x["region"],x["availability-zone"],x["aws_name"],x["environment"],x["env"],x["bu"],x["organization"],x["application_id"],x["instance_type"],x["image"],x["created_by"],x["autoscaling_group"],x["resourcedesc"],x["aws_id"],x["iam_profile"],x["status"]])
        print "Saved report in CSV format to: DATADOG_REPORT.csv"

''' This function removes unnecessary lines from the raw json obtained from DD API '''
def parse_for_json():
        fa = open('all_hosts_from_dd.json', 'r')
        g = open('all_hosts_from_dd_parsed.json', 'w')
        flag = 0

        for line in fa:
        #       line = line.rstrip()
                if "tags_by_source" in line:
                        flag = 1
                if  "}," in line:
                        flag = 0
                if flag == 1:
                        if '{' in line:
                                g.write(line)
                        elif '[' in line:
                                newline=line.replace('[','{')
                                g.write(newline)
                        elif ']' in line:
                                newline=line.replace(']','}')
                                g.write(newline)
                        elif ':' not in line:
                                #pass
                                if ',' in line:
                                        newline=line.replace(',',': "",')
                                else:
                                        newline=line.replace('"\n','": ""\n')
                                g.write(newline)
                        else:
                                newline=line.replace(':','": "',1)
                                g.write(newline)
                elif flag == 0:
                        g.write(line)
        g.close()
        fa.close()
        print "Parsed for proper json format to file : all_hosts_from_dd_parsed.json"

''' This function generates HTML file to send via email from the template under templates dir '''
def generate_html(aws_hosts_count, aws_hosts_without_agent_count):
	file_loader = FileSystemLoader('templates')
	env = Environment(loader=file_loader)
	template = env.get_template('email-template.html')
	output = template.render(aws_count=aws_hosts_count, agent_count=aws_hosts_without_agent_count)

	html_file = open("msg-body.html", "w")
	html_file.write(output)
	html_file.close()

if r.status_code == 200:
        #data = r.json()

        with io.open("all_hosts_from_dd.json",'w', encoding='utf-8') as fa:
                fa.write(json.dumps(r.json(), indent=2, ensure_ascii=False))
        parse_for_json()
        print "Saved all_hosts_from_dd.json"

        with open('all_hosts_from_dd_parsed.json', 'r+') as json_file:
                data = json.load(json_file)
        write_host_info_to_file(data)
