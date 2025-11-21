import inquirer
import json
import subprocess
import sys


def send_apns_payload(device_token, apns_payload):
    try:
        xcrun_command = f"echo '{apns_payload}' | xcrun simctl push {device_token} -"
        subprocess.run(xcrun_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending push notification: {e.stderr}")
        sys.exit(1)


def create_apns_payload(title, body, action, bundle):
    apns_payload = {
        "aps": {
            "alert": {
                "title": title or "Push Notification Title",
                "body": body or "Push Notification Body",
                "sound": "bingbong.aiff",
            },
            "badge": 1,
        },
        "gcm.message_id": "firebase-id",
        "priority": "high",
        "content_available": True,
        "mutable_content": True,
        "id": "mock-push-notification-id",
        "action": action or "",
        "Simulator Target Bundle": bundle,
    }

    return json.dumps(apns_payload)


def get_simulator_devices():
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        devices = json.loads(result.stdout)
        available_devices = []

        for _, device_list in devices["devices"].items():
            for device in device_list:
                if "state" in device:
                    model = device["name"]
                    udid = device["udid"]
                    if model.startswith("iPhone"):
                        print(f"- Model: {model}, Device Token: {udid}")
                        available_devices.append((model, udid))

        return available_devices
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving simulator devices: {e.stderr}")
        return []


def get_bundle_identifiers(device_udid):
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "listapps", device_udid],
            check=True,
            capture_output=True,
            text=True,
        )
        bundle_choices = []

        for line in result.stdout.splitlines():
            if "CFBundleIdentifier" in line:
                start_index = line.find('"') + 1
                end_index = line.find('"', start_index)
                cf_bundle_identifier = line[start_index:end_index]
                bundle_choices.append(cf_bundle_identifier)

        return bundle_choices
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving bundle identifiers: {e.stderr}")
        return []


if __name__ == "__main__":
    available_devices = get_simulator_devices()

    if len(available_devices) == 0:
        print(
            "No devices found. Make sure your simulator device is available, then run the program again."
        )
        sys.exit(0)

    device_token = inquirer.list_input(
        "Select the device token", choices=available_devices
    )

    bundle_choices = get_bundle_identifiers(device_token)

    if len(bundle_choices) == 0:
        print(
            "No apps installed. Make sure your simulator device has apps installed, then run the program again."
        )
        sys.exit(0)

    bundle = inquirer.list_input(
        "Select the bundle identifier:", choices=bundle_choices
    )
    title = inquirer.text(
        message="Enter the push notification title (default: Push Notification Title)"
    )
    body = inquirer.text(
        message="Enter the push notification body (default: Push Notification Body)"
    )
    action = inquirer.text(message="Enter the action")

    apns_payload = create_apns_payload(title, body, action, bundle)
    send_apns_payload(device_token, apns_payload)
