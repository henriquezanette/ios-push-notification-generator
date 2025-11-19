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
