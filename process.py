import json
import time
from datetime import datetime
import math
import pandas as pd
import plotly.express as px

# get env variables
from config import config_details
key_path=config_details['key_path']
project_path=config_details['project_path']
audio_file_name=config_details['audio_file_name']

def main():
    chart_timeline()
    get_df_segment_items()
    get_df_items()

def load_json():
    fname = 'debate_audio.mp3.json'
    with open(fname, 'rt') as f:
        content = f.read()
        data = json.loads(content)
        content = None

    return data

# convert seconds to faux datetime for Plotly timeline x-axis
def get_datetime(seconds):
    hhmmss = time.strftime('%H:%M:%S', time.gmtime(int(math.ceil(float(seconds)))))
    date_string = '1970-01-01 ' + str(hhmmss)
    date_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    return date_time

# each speaker has multiple segments which has start time, end time
def get_df_segments():
    segment_list = []
    data = load_json()

    for segment in data['results']['speaker_labels']['segments']:
        segment_dict = {'speaker_label': segment['speaker_label'], 'speaker_num': segment['speaker_label'][-1:],'start_time': segment['start_time'], 'end_time':segment['end_time'], 'start_date_time': get_datetime(segment['start_time']), 'end_date_time': get_datetime(segment['end_time']) }
        segment_list.append(segment_dict)
    
    df_segments = pd.DataFrame(segment_list)
    df_segments.replace({'speaker_label': {'spk_0':'Wallace','spk_1': 'Biden','spk_2': 'Trump'}}, regex=False, inplace=True)

    df_segments.to_csv('df_segments.csv', sep=',', encoding='utf-8')

    print(df_segments.head(5))
    return df_segments

# each speaker segment has multiple items each with single word with start time and end time
def get_df_segment_items():
    segment_item_list = []
    data = load_json()

    for segment in data['results']['speaker_labels']['segments']:
        for item in segment['items']:
            segment_item = {'speaker_label': item['speaker_label'], 'speaker_num': item['speaker_label'][-1:],'start_time': item['start_time'], 'end_time':item['end_time']}
            segment_item_list.append(segment_item)
    
    df_segment_items = pd.DataFrame(segment_item_list)
    df_segment_items.replace({'speaker_label': {'spk_0':'Wallace','spk_1': 'Biden','spk_2': 'Trump'}}, regex=False, inplace=True)

    df_segment_items['speaker_num'] = df_segment_items['speaker_num'].astype(int)

    # get speaker segment start_time
    df_segment_items['speaker_change_index'] = df_segment_items['speaker_num'].diff()
    df_segment_items['segment_start_time'] = df_segment_items.loc[df_segment_items['speaker_change_index'] != 0, 'start_time']
    df_segment_items['segment_start_time'].fillna(method='ffill', inplace=True)

    # get speaker segment end_time
    df_segment_items['speaker_change_index'] = df_segment_items['speaker_num'].diff(-1)
    df_segment_items['segment_end_time'] = df_segment_items.loc[df_segment_items['speaker_change_index'] != 0, 'end_time']
    df_segment_items['segment_end_time'].fillna(method='backfill', inplace=True)
     
    df_segment_items.to_csv('df_segment_items.csv', sep=',', encoding='utf-8')

    #print(df_segment_items.head(5))
    return df_segment_items

# get separate items each which has start time, end time, type and one or more alternative.content (actual word transcribed), alternative.confidence (0 to 1) =>just get first alternative
def get_df_items():
    item_list = []
    data = load_json()

    for item in data['results']['items']:
        try:
            result_item = {
                'start_time': item['start_time'], 
                'end_time': item['end_time'], 
                'content': item['alternatives'][0]['content'] 
            }
            item_list.append(result_item)
        except:
            pass
    
    df_items = pd.DataFrame(item_list)

    df_items.to_csv('df_items.csv', sep=',', encoding='utf-8')

    print(df_items.head(5))
    return df_items

# create Plotly timeline chart
def chart_timeline():
    df = get_df_segments()
    color_dem = "#0015BC"
    color_gop = "#E9141D"
    color_mod = "#000"
    color_map = {"Wallace": color_mod, "Biden": color_dem, "Trump": color_gop}
    color_lines = "#AAAAAA"  # color of axes and marker outlines
    project_path=config_details['project_path']

    fig = px.timeline(
        df, 
        x_start="start_date_time", 
        x_end="end_date_time", 
        y="speaker_label", 
        color="speaker_label",
        color_discrete_map=color_map,
        width=1000, 
        height=300
    )

    fig.update_layout(
        {
            "plot_bgcolor": "#fff",
            "paper_bgcolor": "#fff",
            "title": {
                "text": "Presidential Debate #1 Speaker Segments From CSPAN Video - created by 009co.com",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            "font": dict(color="#666", size=10,),
            "showlegend": False,
        }
    )

    fig.update_xaxes(
        dict(
            title_text="", 
            linecolor='#FFF', 
            showgrid=True,
            tickformat="%H:%M",
            #tickmode = 'linear',
            #tick0 = 0,
            #dtick = 10,
        ),
        tickfont=dict(size=10),
    )

    fig.update_yaxes(
        dict(
            title_text="",
            visible=True,
            #linecolor=color_lines,
            #showgrid=False,
            #tickformat=',d',
        ),
        tickfont=dict(size=12),
    )

    chart_output_file = '2020_debate_1_timeline.png'
    fig.write_image(project_path + chart_output_file)

if __name__ == '__main__':
     main()