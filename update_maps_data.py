import pandas as pd
import boto3
import botocore
from shapely.geometry import Point, shape
import json


BUCKET = 'seattle-911-data'
filename = 'df_72hr.csv'
neighborhoods_geojson = 'static/seattle_neighborhoods.geojson'


def retrieve_72hr_dataframe(filename):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(BUCKET).download_file(filename, 'static/' + filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    df = pd.read_csv('static/' + filename)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df


def add_hoods_df(df, geojson):
    with open(geojson) as f:
        features = json.load(f)['features']
    idx = 1
    for index, series in df.iterrows():
        point = Point((float(series.longitude), float(series.latitude)))
        for feature in features:
            if shape(feature["geometry"]).buffer(0).contains(point):
                df.loc[idx, 'neighborhood'] = feature['properties']['name']
        idx += 1
    df = df.dropna()
    return df


def create_incident_list(df):
    incident_list = df['incident_type'].unique().tolist()
    incident_list.sort()
    incident_list.insert(0, 'All Incidents')
    with open("static/incident_list.txt", 'w') as f:
        for incident in incident_list:
            f.write(incident + '\n')
    # with open("static/incident_list.txt", 'r') as f:
    #     incident_list = [line.rstrip('\n') for line in f]
    return 1


def update_maps_data(filename, neighborhoods_geojson):
    df = retrieve_72hr_dataframe(filename)
    df = add_hoods_df(df, neighborhoods_geojson)
    create_incident_list(df)
    df.to_csv("static/df_72hr.csv")
    return 1


update_maps_data(filename, neighborhoods_geojson)
