from shapely.geometry import Point
import pandas as pd
import folium
from folium import plugins
import plotly.express as px

csv_data = 'static/df_72hr.csv'


def generate_heatmap(incident_df):
    point_list=[]
    for index, series in incident_df.iterrows():
        new_point = Point(series.longitude, series.latitude)
        point_list.append(new_point)
    incident_df['geometry'] = point_list
    m = folium.Map(location=[47.608, -122.335], tiles='Cartodb dark_matter', zoom_start=13)
    heat_data = [[point.xy[1][0], point.xy[0][0]] for point in incident_df.geometry]
    plugins.HeatMap(heat_data).add_to(m)
    m.save('static/heat_map.html')
    return 1


def generate_incident_sunburst(incident_df):
    """Generates sunburst graph and stores it in static file"""
    df = incident_df.incident_type.value_counts().rename_axis('incident').reset_index(name='counts')
    fire_list = ['Automatic Fire Alarm Resd', 'Auto Fire Alarm', 'Bark Fire', 'Brush Fire Freeway', 'Car Fire',
                 'Fire in Building', 'Rubbish Fire', 'Brush Fire', 'Dumpster Fire', 'Illegal Burn',
                 'Encampment Fire',
                 'Automatic Fire Alarm False', ]
    medical_list = ['Triaged Incident', 'Nurseline/AMR', 'Aid Response', 'Mutual Aid- Aid', 'BC Aid Response',
                    'Aid Response Yellow', 'Medic Response- Overdose', 'Medic Response- 6 per Rule',
                    'Single Medic Unit',
                    'BC Medic Response- 6 per rule', 'Medic Response', 'Medic Response- 7 per Rule']
    police_list = ['Scenes Of Violence 7', '4RED - 2 + 1 + 1', 'MVI - Motor Vehicle Incident', 'Encampment Aid',
                   '1RED 1 Unit', 'AFA4 - Auto Alarm 2 + 1 + 1', 'MVI Freeway']

    incident_type_list = []
    for incident in df.incident:
        if incident in fire_list:
            incident_type = 'Fire'
        elif incident in medical_list:
            incident_type = 'Medical'
        elif incident in police_list:
            incident_type = 'Police'
        else:
            incident_type = 'Other'
        incident_type_list.append(incident_type)

    df['incident_type'] = incident_type_list

    fig = px.sunburst(df, path=['incident_type', 'incident'], values='counts',

                      color_continuous_scale='Turbo'
                      )
    fig.write_html('static/sunburst.html')
    return 1


def generate_incident_histogram():
    fire_list = ['Automatic Fire Alarm Resd', 'Auto Fire Alarm', 'Bark Fire', 'Brush Fire Freeway', 'Car Fire',
                 'Fire in Building', 'Rubbish Fire', 'Brush Fire', 'Dumpster Fire', 'Illegal Burn',
                 'Encampment Fire',
                 'Automatic Fire Alarm False', ]
    medical_list = ['Triaged Incident', 'Nurseline/AMR', 'Aid Response', 'Mutual Aid- Aid', 'BC Aid Response',
                    'Aid Response Yellow', 'Medic Response- Overdose', 'Medic Response- 6 per Rule',
                    'Single Medic Unit',
                    'BC Medic Response- 6 per rule', 'Medic Response', 'Medic Response- 7 per Rule']
    police_list = ['Scenes Of Violence 7', '4RED - 2 + 1 + 1', 'MVI - Motor Vehicle Incident', 'Encampment Aid',
                   '1RED 1 Unit', 'AFA4 - Auto Alarm 2 + 1 + 1', 'MVI Freeway']
    incident_type_list = []
    df = pd.read_csv(csv_data, index_col=0)
    df['datetime'] = pd.to_datetime(df['datetime'])
    for incident in df.incident_type:
        if incident in fire_list:
            incident_type = 'Fire'
        elif incident in medical_list:
            incident_type = 'Medical'
        elif incident in police_list:
            incident_type = 'Police'
        else:
            incident_type = 'Other'
        incident_type_list.append(incident_type)

    df['incident_cat'] = incident_type_list
    fig = px.histogram(df, x='datetime', color='incident_cat', hover_data=df.columns, nbins=48)
    fig.write_html('static/histogram.html')
    return 1


def create_maps(data):
    df = pd.read_csv(data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    generate_heatmap(df)
    generate_incident_histogram()
    generate_incident_sunburst(df)
    return 1


create_maps(csv_data)
