import googleapiclient.discovery
import logging
import traceback
import base64
import json
from google.auth import compute_engine

# qui mi serve per recupere le credenziali dal serviceaccount
credentials = compute_engine.Credentials()
compute = googleapiclient.discovery.build('compute', 'v1')

logging.basicConfig(encoding='utf-8', level=logging.INFO)

def tag_instance(instance: str, project: str, zone: str):
    # tag (label) the instance and return a list of the disk volumes
    instance_information = compute.instances().get(project=project, zone=zone, instance=instance).execute()
    instance_disks_list = [disk['deviceName'] for disk in instance_information['disks']]

    # recupera le label precedenti in modo da andare in append
    instance_fingerprint = instance_information['labelFingerprint']
    # https://cloud.google.com/compute/docs/reference/rest/v1/instances/setLabels#request-body
    instances_set_labels_request_body = {'labels': {'acronimo': 'skrt0'}, 'labelFingerprint': instance_fingerprint}
    request = compute.instances().setLabels(project=project, zone=zone, instance=instance, body=instances_set_labels_request_body)
    try:
        request.execute()
        return {'status': True, 'instance_disks_list': instance_disks_list}
    except Exception as e:
        logging.error(str(e))
        return {'status': False, instance_disks_list: []}


def tag_disks(disks_list: list, project: str, zone: str, instance_name):
    # tag a volume from the instance volume list
    for disk in disks_list:
        logging.info(f'going to tag disk {disk}')
        try:
            disk_data = compute.disks().get(project=project, zone=zone, disk=disk).execute()
        # if the instance is part of instace template - the api volume name is the instance template name, but the actual volume name is the instance name
        except googleapiclient.errors.HttpError:
            disk_data = compute.disks().get(project=project, zone=zone, disk=instance_name).execute()
            disk = instance_name
        disk_fingerprint = disk_data['labelFingerprint']
        disk_set_labels_request_body = {'labels': {'acronimo': 'skrt0', 'instance': instance_name}, 'labelFingerprint': disk_fingerprint}

        try:
            compute.disks().setLabels(project=project, zone=zone, resource=disk, body=disk_set_labels_request_body).execute()
        except Exception as e:
            logging.error(str(e))
    return True

def hello_pubsub(event, context):
    # parse the pubsub event
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logging.debug(f'Dump del messaggio ' + pubsub_message)
    pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    
    try:
        # alternative method 
        # project_id = pubsub_message.get('resource').get('labels').get('project_id')
        project_id = pubsub_message['resource']['labels']['project_id']
        logging.debug(f"Founded - project_id: " + project_id)
        instance_name = pubsub_message['protoPayload']['request']['name']
        # è una lista di zone, anche se con un elemento, da approfondire
        logging.debug(f"Founded - instance_name: " + instance_name)
        instance_zone = pubsub_message['protoPayload']['resourceLocation']['currentLocations'][0]
        logging.debug(f"Founded - instance_zone: " + instance_zone)
        # attenzione che la mail non è un valore valido per le label
        user_email = pubsub_message['protoPayload']['authenticationInfo']['principalEmail']
        logging.debug(f"Founded - user_email: " + user_email)
        logging.info(f'new instance created by {user_email}, going to tag instance {instance_name} on project {project_id} and zone {instance_zone}')
    except Exception as e:
        traceback.print_exc()
        logging.error(f"null values founded, skip label operations !!!")
        exit()

    instance_tag = tag_instance(instance_name, project_id, instance_zone)
    
    # if instance tag was successful and the instance volume list exists
    if instance_tag and instance_tag['instance_disks_list']:
        disks_list = instance_tag['instance_disks_list']
        # tag volumes
        disks_tag = tag_disks(disks_list, project_id, instance_zone, instance_name)
        if disks_tag:
            return True

    logging.info(f'Instance {instance_name} labeled')