import json
import base64
import boto3

# Create Rekognition client
rekognition = boto3.client("rekognition")


def lambda_handler(event, context):

    try:
        # Get request body from API Gateway
        body = event.get("body", "{}")

        # Convert JSON string into Python dictionary
        if isinstance(body, str):
            body = json.loads(body)

        # Get Base64 image from request
        image_base64 = body["image"]

        # Convert Base64 image into bytes
        image_bytes = base64.b64decode(image_base64)

        # Send image to Amazon Rekognition
        response = rekognition.detect_faces(
            Image={
                "Bytes": image_bytes
            },
            Attributes=["DEFAULT"]
        )

        # Count detected faces
        face_count = len(response["FaceDetails"])

        # Print result in CloudWatch
        print("================================")
        print("FACE DETECTION RESULT")
        print("Number of faces detected:", face_count)
        print("================================")

        # Send result back to API Gateway
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "face_count": face_count
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }