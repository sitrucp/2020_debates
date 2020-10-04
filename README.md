# 2020 Presidential Debate #1 Speaker Segments - Using Amazon Transcribe

Amazon Transcribe was used to create a transcription of the 2020 Presidential Debate #1 audio.

## Retrieving debate audio

Debate audio was retrieved from this CSPAN <a href="https://www.youtube.com/watch?v=wW1lY5jFNcQ">YouTube video</a> using youtube-dl.

<a href="https://youtube-dl.org">youtube-dl</a> is a command-line program to download videos from YouTube.com.

The audio was retrieved using youtube-dl using following command:

youtube-dl -x --audio-format "mp3" "https://www.youtube.com/watch?v=wW1lY5jFNcQ"


## Transcribing debate audio

Amazon Transcribe requires the audio file to be in an S3 bucket. The mp3 file was uploaded to a bucket and Amazon Transcribe used to transcribe the audio. Both were done using AWS Boto3 SDK.

The transcription process outputs a JSON file into the S3 bucket. The JSON file contains the following:

* Text transcription - text of audio transcription.
* Speaker segments - one or more time based segments by speaker.  
* Segment items - one or more time based "items" (each a single word) by speaker.

## Processing debate output JSON

Python used to load JSON file into Pandas dataframe that was used as data source for Plotly Timeline chart.

Timeline charts require datetimes for period start and end and x-axis values. A fake date was created by adding arbitrary date (1970-01-01) to an "HH:mm:ss" value created from the segment start_time and end_time seconds values.

