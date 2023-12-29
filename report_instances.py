import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import storage

# Replace with your GCP project and service account credentials JSON file
project_id = "turing-ember-399111"
service_account_file = "turing-ember.json"
bucket_name = "sql_assets"  # Replace with your Cloud Storage bucket name

def get_instance_data(project_id, service_account_file, bucket_name):
    # Authenticate with GCP using service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Create a CSV file to store the instance data
    csv_file = "instance_data.csv"

    with open(csv_file, "w", newline="") as csvfile:
        fieldnames = ["Instance Name", "Instance IP", "Instance State", "Region"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        compute = build("compute", "v1", credentials=credentials)

        # Get a list of all zones in the project
        zones = compute.zones().list(project=project_id).execute()

        if "items" in zones:
            for zone in zones["items"]:
                zone_name = zone["name"]
                instances = compute.instances().list(project=project_id, zone=zone_name).execute()

                if "items" in instances:
                    for instance in instances["items"]:
                        instance_name = instance["name"]
                        instance_ip = instance.get("networkInterfaces", [{}])[0].get("networkIP", "")
                        instance_status = instance.get("status", "")
                        writer.writerow(
                            {
                                "Instance Name": instance_name,
                                "Instance IP": instance_ip,
                                "Instance State": instance_status,
                                "Region": zone_name,
                            }
                        )

    print(f"Instance data saved to {csv_file}")

    # Upload the CSV file to Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("instance_data.csv")
    blob.upload_from_filename(csv_file)

    print(f"CSV file uploaded to {bucket_name}/instance_data.csv")

# Call the function to retrieve instance data and store in Cloud Storage
get_instance_data(project_id, service_account_file, bucket_name)
