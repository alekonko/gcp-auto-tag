import json

data = {
    "owner": {
        "name": "Alekonko",
        "species": "Human"
    }
}

with open("hacks/data_file.json", "w") as write_file:
    json.dump(data, write_file)

json_string = json.dumps(data, indent=4)

print(json_string)

with open("hacks/sample_event.json", "r") as read_file:
    pubsub_message = json.load(read_file)
# attention, original pubsub use
# pubsub_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))

project_id = pubsub_message['resource']['labels']['project_id']
instance_name = pubsub_message['protoPayload']['request']['name']
# è una lista di zone, anche se con un elemento, da approfondire
instance_zone = pubsub_message['protoPayload']['resourceLocation']['currentLocations'][0]
# attenzione che la mail non è un valore valido per le label
user_email = pubsub_message['protoPayload']['authenticationInfo']['principalEmail']

print("A new Compute instance is been created by " + user_email + " on project: " + project_id + ", instance name:" + instance_name + ", on zone: " + instance_zone + ". We need a label :) ")



print("end")