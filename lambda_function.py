import json
import base64
import boto3
import uuid

rekognition = boto3.client("rekognition")
polly = boto3.client("polly")
s3 = boto3.client("s3")

BUCKET_NAME = "samshru"


def lambda_handler(event, context):
    try:
        # Get request body
        body = event.get("body", "{}")

        if isinstance(body, str):
            body = json.loads(body)

        # Get Base64 image
        image_base64 = body["image"]

        # Convert Base64 to image bytes
        image_bytes = base64.b64decode(image_base64)

        # Detect faces using Rekognition
        response = rekognition.detect_faces(
            Image={"Bytes": image_bytes},
            Attributes=["DEFAULT"]
        )

        face_count = len(response["FaceDetails"])

        # Create text for Polly
        if face_count == 0:
            speech_text = "No faces were detected in the image."
        elif face_count == 1:
            speech_text = "One face was detected in the image."
        else:
            speech_text = f"{face_count} faces were detected in the image."

        # Convert text to speech using Polly
        polly_response = polly.synthesize_speech(
            Text=speech_text,
            OutputFormat="mp3",
            VoiceId="Joanna"
        )

        # Generate unique MP3 filename
        audio_key = f"face-detection-audio/{uuid.uuid4()}.mp3"

        # Upload MP3 to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=audio_key,
            Body=polly_response["AudioStream"].read(),
            ContentType="audio/mpeg"
        )

        print("================================")
        print("FACE DETECTION RESULT")
        print("Number of faces detected:", face_count)
        print("Speech:", speech_text)
        print("Audio stored in S3:", audio_key)
        print("================================")

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "face_count": face_count,
                "message": speech_text,
                "audio_file": audio_key
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
