import json
import traceback
import logging
import sys

# data = {
#     "owner": {
#         "name": "Alekonko",
#         "species": "Human"
#     }
# }
# with open("data_file.json", "w") as write_file:
#     json.dump(data, write_file)
# json_string = json.dumps(data, indent=4)
# print(json_string)

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

with open("sample_event.json", "r") as read_file:
    pubsub_message = json.load(read_file)
# attention, original pubsub use
# pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))

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
    #print(str(e))

