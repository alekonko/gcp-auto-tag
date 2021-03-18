# GCP Autolaber Reloaded 2021 - Autolabel object, adapted for GCP 03/2021

Function che aggiunge custom label (es. label acronimo) alle istanze e relativi dischi quando intercetta una creazione di istanza compute engine.

Adattato codice e configurazioni da [Orginal version](https://github.com/doitintl/gcp-auto-tag), attualmente non piu funzionanti per passaggio da Stackdriver a Cloud Log

Original Idea, references:

- [Autolabel object for](https://blog.doit-intl.com/automatically-label-google-cloud-compute-engine-instances-and-disks-upon-creation-5d1245f361c1)

Descrizione scenario:

- in fase di creazione compute instance vengono generati di log di audit che sono inviati in una coda pub/sub.
- la function è istanziata dai messaggi nella coda

DONE:

- Change Skink syntax (add filter for a custom project) for new cloudlog
- fix python code to new json scheme
- Add label "acronimo: skrt0" (attenzione, label minuscole)
- add logging and basic error handling

## GCP Configurations Step

- Create roles and serviceaccounts

```bash
# Replace $MY_PROJECT with your project id

SERVICE_ACCOUNT=autolabel_instances
MY_PROJECT=ocp-isolated

gcloud iam roles create $SERVICE_ACCOUNT  --title=autolabel-instances --project $MY_PROJECT --description='cloud function service account to add acronimo label' --permissions=compute.disks.get,compute.disks.setLabels,compute.instances.get,compute.instances.setLabels --stage=GA
gcloud iam service-accounts create autolabel-instances

gcloud projects add-iam-policy-binding $MY_PROJECT --member serviceAccount:autolabel-instances@$MY_PROJECT.iam.gserviceaccount.com --role projects/$MY_PROJECT/roles/$SERVICE_ACCOUNT
gcloud projects add-iam-policy-binding $MY_PROJECT --member serviceAccount:autolabel-instances@$MY_PROJECT.iam.gserviceaccount.com --role roles/logging.logWriter
```

- Creare sink da usare, adeguato con Cloud Log (son cambiati i json da Stackdriver!!) 03/2021

- formato sink (è cambiato formato json del logging)  [router](https://console.cloud.google.com/logs/router?project=ocp-isolated)

object-to-label-sink -> importante avere log univoco, importante operation.first="true" !!

```conf
resource.type="gce_instance"
resource.labels.project_id="ocp-isolated"
protoPayload.methodName="beta.compute.instances.insert"
operation.first="true"
```

## Misc

setting authentication outside cloudshell or function

```bash
export GOOGLE_APPLICATION_CREDENTIALS="~/.gcp/osServiceAccount.json"
```

```bash
gcloud beta compute --project=ocp-isolated instances create vmtolabel006 --zone=europe-west3-c --machine-type=f1-micro --subnet=subnet-eu-west-3 --no-address --maintenance-policy=MIGRATE --service-account=351803534639-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --image=debian-10-buster-v20210217 --image-project=debian-cloud --boot-disk-size=10GB --boot-disk-type=pd-balanced --boot-disk-device-name=vmtolabel005 --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
```
