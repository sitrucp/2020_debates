import boto3
from botocore.exceptions import ClientError
import sys

# get env variables
from config import config_details
key_path=config_details['key_path']
project_path=config_details['project_path']
audio_file_name=config_details['audio_file_name']
region_name=config_details['region_name'] 
bucket_name=config_details['bucket_name'] 

# get aws credentials
sys.path.insert(0, key_path)
from aws_keys import debate_transcribe_keys
AWS_KEY=debate_transcribe_keys['AWS_KEY']
AWS_SECRET=debate_transcribe_keys['AWS_SECRET']

s3_client=boto3.client(
    's3',
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET
)

def main():
    upload_flag=False
    if upload_flag:
        upload_file()
    else:
        start_transcription(wait_process=False)

def upload_file():
    response=s3_client.upload_file(project_path + audio_file_name, bucket_name, audio_file_name)

def start_transcription(wait_process=True):
    job_name=audio_file_name
    file_uri='https://' + bucket_name + '.s3.amazonaws.com/' + audio_file_name

    transcribe_client=boto3.client(
        'transcribe',
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        region_name=region_name
    )

    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp3',
        LanguageCode='en-US',
        OutputBucketName=bucket_name,
        Settings={'MaxSpeakerLabels': 3,'ShowSpeakerLabels': True})
    if wait_process:
        while True:
            status=transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print('Not ready yet...')
            time.sleep(20)

        print('Transcription finished')
        return status

if __name__ == '__main__':
    main()
    