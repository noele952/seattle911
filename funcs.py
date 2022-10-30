# import boto3
import pandas as pd
# from botocore.exceptions import ClientError
import folium
import json
from shapely.geometry import shape


# AWS_DEFAULT_REGION = 'us-east-1'
# ssm = boto3.client('ssm', AWS_DEFAULT_REGION)
#
#
# def get_parameters(parameter_name):
#     prefix = '/seattle911/'
#     parameter = ssm.get_parameter(Name = prefix + parameter_name)['Parameter']['Value']
#     print(parameter)
#     return parameter


def create_sns_message(name, email, message):
    message = name + '\n' + email + '\n' + message
    return message

#
# def publish_sns_message(topic_arn, message):
#     """
#     Publishes a message to a topic.
#     """
#     sns = boto3.client('sns', region_name=AWS_DEFAULT_REGION)
#     subject = 'Seattle 911 Contact Form'
#     try:
#
#         response = sns.publish(
#             TopicArn=topic_arn,
#             Message=message,
#             Subject=subject,
#         )['MessageId']
#     except ClientError as err:
#         print(err)
#     else:
#         return response


def get_incident_list():
    with open("static/incident_list.txt", 'r') as f:
        incident_list = [line.rstrip('\n') for line in f]
    return incident_list


def create_neighborhood_list(df):
    neighborhood_list = []
    for index, series in df.iterrows():
        if series.city == 'Seattle':
            neighborhood_list.append(series['name'])
    neighborhood_list.sort(reverse=True)
    neighborhood_list.insert(0, 'Entire City')
    return neighborhood_list


def create_geojson_df_csv(geojson):
    with open(geojson) as f:
        features = json.load(f)['features']
    center_lon = [shape(feature["geometry"]).buffer(0).centroid.x for feature in features]
    center_lat = [shape(feature["geometry"]).buffer(0).centroid.y for feature in features]
    name = [feature['properties']['name'] for feature in features]
    city = [feature['properties']['city'] for feature in features]
    geometry = [feature['geometry'] for feature in features]
    zipped = list(zip(name, city, center_lon, center_lat, geometry))
    df = pd.DataFrame(zipped, columns=['name', 'city', 'center_lon', 'center_lat', 'geometry'])
    return df


def create_incident_map(current_incident, neighborhood, incident_df, geojson_df):
    if neighborhood == 'Entire City':
        m = folium.Map(location=[47.608, -122.335], zoom_start=12)
    else:

        m = folium.Map(location=[geojson_df[geojson_df.name == neighborhood].center_lat,
                                 geojson_df[geojson_df.name == neighborhood].center_lon],
                       zoom_start=15)

        with open('static/seattle_neighborhoods.geojson') as f:
            features = json.load(f)['features']
        for feature in features:
            if feature['properties']['name'] == neighborhood:
                folium.GeoJson(feature['geometry'], name='geojson').add_to(m)
    for index, series in incident_df.iterrows():
        if current_incident == 'All Incidents':
            folium.Marker(
                location=[series['latitude'], series['longitude']],
                popup=series['marker_text'],
                icon=folium.Icon(color=series['color'], icon=series['icon'], prefix='fa'),
            ).add_to(m)
        else:
            if series['incident_type'] == current_incident:
                folium.Marker(
                    location=[series['latitude'], series['longitude']],
                    popup=series['marker_text'],
                    icon=folium.Icon(color=series['color'], icon=series['icon'], prefix='fa'),
                ).add_to(m)
    return m
