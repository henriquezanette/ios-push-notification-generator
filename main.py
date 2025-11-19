import inquirer
import json
import subprocess
import sys


def send_apns_payload(device_token, apns_payload):
    xcrun_command = f"echo '{apns_payload}' | xcrun simctl push {device_token}"
    subprocess.run(xcrun_command, shell=True)


def create_apns_payload(title, body, action, bundle):
    apns_payload = {
        "aps": {
            "alert": {
                "title": title or "Push Notification Title",
                "body": body or "Push Notification Body",
                "sound": "bingbonf.aiff",
            },
            "badge": 1,
        },
        "gcm.message_id": "firebase-id",
        "priority": "high",
        "content-available": True,
        "mutable_content": True,
        "id": "mock-push-notification-id",
        "action": action,
        "Simulator Target Bundle": bundle,
    }

    return json.dumps(apns_payload)


def get_simulator_devices(available_devices):
    result = subprocess.run(
        ["xcrun", "simctl", "list", "devices", "booted", "--json"],
        capture_output=True,
        text=True,
    )
    devices = json.loads(result.stdout)

    for device_list in devices["devices"].items():
        for device in device_list:
            if "state" in device:
                model = device["name"]
                udid = device["udid"]
                if model.startswith("iPhone"):
                    print(f"- Model: {model}, Device Token: {udid}")
                    available_devices.append((model, udid))


def get_bundle_identifiers(bundle_choices, device_udid):
    output = subprocess.check_output(["xcrun", "simctl", "listapps", device_udid])
    output_options = output.decode("utf-8").splitlines()

    for line in output_options:
        if "CFBundleIdentifier" in line:
            start_index = line.find('"') + 1
            end_index = line.find('"')
            cf_bundle_identifier = line[start_index:end_index]

            bundle_choices.append(cf_bundle_identifier)
