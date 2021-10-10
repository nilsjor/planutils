import json
from collections import OrderedDict
import glob
import os

service_templates={}

def load_json(f_name):
    with open(f_name, 'r') as f:
        json_body = json.load(f,object_pairs_hook=OrderedDict)
    return json_body

def save_json(f_name,f_content):
    with open(f_name, 'w') as f:
        f.write(json.dumps(f_content,indent=4, sort_keys=False, separators=(',', ': ')))

def load_template():
    service_templates={}
    templates_name_list=glob.glob('*.json')
    for template_file_name in templates_name_list:
        template_name=template_file_name.split(".")[0]
        service_template_body=load_json(template_file_name)
        service_templates[template_name]=service_template_body
    return service_templates

def get_template(template_name):
    if template_name=="planner":
        return service_templates["planner"].copy()
    return False

def generate_full_manifest(manifest,package_name):
    manifest_full=manifest.copy()
    for service in manifest["endpoint"]["services"]:
        service_body=manifest["endpoint"]["services"][service]
        if "template" in service_body:
            template_name=service_body["template"]
            template=get_template(template_name)
            new_service_body=template.copy()
            # update addtional args
            for key in template:
                if key in service_body:
                    if key=="args":
                        for arg in service_body["args"]:
                            new_service_body["args"].append(arg)
                    else:
                        #update call, return
                        new_service_body[key]=service_body[key]
            new_service_body["call"]=new_service_body["call"].replace("{package_name}",package_name)
            manifest_full["endpoint"]["services"][service]=new_service_body
    return manifest_full

service_templates=load_template()
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__)).replace("/TEMPLATE/SERVICE_TEMPLATE","")

# generate full manifest if manifest_compact.json is provided
for conf_file in glob.glob(os.path.join(PACKAGE_DIR, '*')):
    base = os.path.basename(conf_file)
    if base not in ['README.md', 'TEMPLATE']:
        manifest_compact_loc=os.path.join(conf_file, 'manifest_compact.json')
        manifest_full_loc=os.path.join(conf_file, 'manifest.json')
        if os.path.exists(manifest_compact_loc):
            manifest_compact=load_json(manifest_compact_loc)
            manifest_full=generate_full_manifest(manifest_compact,base)
            save_json(manifest_full_loc,manifest_full)




            
