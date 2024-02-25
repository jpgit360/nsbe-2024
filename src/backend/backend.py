# libraries related to flask
from flask import Flask, jsonify, Response, render_template, request

# general libraries
from dataclasses import dataclass
from typing import Dict, List
from dataclasses import asdict
import json
import io

# math libraries
import pandas as pd
import io
from numpy import nan
import numpy as np
from math import isnan
import plotly
import plotly.express as px
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import openpyxl
from flask_cors import CORS

#api libraries
from positionstack_api import API_KEY
import http.client, urllib.parse

app = Flask(__name__, template_folder='template')
CORS(app)

@dataclass
class DistrictInfo:
    ppc_stot: int
    pred_cost: int
    funding_gap: int
    outcome_gap: int
    enroll: int
    year: int
    state: str = ""

class SchoolDistrict:
    def __init__(self) -> None:
        self.districts: Dict[str, List[DistrictInfo]] = {}
        self.df = pd.read_excel("./data/SchoolDistricts.xlsx", sheet_name="Data")
        self.df_avg_data = pd.read_csv("./data/dataset_by_avgs.csv")
        self.df_avg_year_data = pd.read_csv("./data/avg_by_year.csv")
        self.avg_plot = None

    def set_data(self) -> None:
        for i in range(len(self.df)):
            curr_district = DistrictInfo(
                int(self.df.loc[i, 'ppcstot']) if not isnan(self.df.loc[i, 'ppcstot']) else 0,
                int(self.df.loc[i, 'predcost']) if not isnan(self.df.loc[i, 'predcost']) else 0,
                int(self.df.loc[i, 'fundinggap']) if not isnan(self.df.loc[i, 'fundinggap']) else 0,
                int(self.df.loc[i, 'outcomegap']) if not isnan(self.df.loc[i, 'outcomegap']) else 0,
                int(self.df.loc[i, 'enroll']) if not isnan(self.df.loc[i, 'enroll']) else 0,
                int(self.df.loc[i, 'year']) if not isnan(self.df.loc[i, 'year']) else 0,
                str(self.df.loc[i, 'state_name'])
            )

            if self.df.loc[i, 'district'] in self.districts:
                self.districts[self.df.loc[i, 'district']].append(curr_district)
            else:
                self.districts[self.df.loc[i, 'district']] = [curr_district]
        
        df2 = self.df_avg_data
        for i in range(len(self.df_avg_data)):
            curr_district = DistrictInfo(
                int(df2.loc[i, 'ppcstot']) if not isnan(df2.loc[i, 'ppcstot']) else 0,
                int(df2.loc[i, 'predcost']) if not isnan(df2.loc[i, 'predcost']) else 0,
                int(df2.loc[i, 'fundinggap']) if not isnan(df2.loc[i, 'fundinggap']) else 0,
                int(df2.loc[i, 'outcomegap']) if not isnan(df2.loc[i, 'outcomegap']) else 0,
                int(df2.loc[i, 'enroll']) if not isnan(df2.loc[i, 'enroll']) else 0,
                0,
                str(df2.loc[i, 'state_name'])
            )
            
            self.districts[df2.loc[i, 'district']].append(curr_district)

        print("Completed populating data...")

    def get_all_data(self):
        return self.districts
    
    def get_specific_district_data(self, name):
        district_data = self.df_avg_data[self.df_avg_data['district'] == name]
        
        curr_district = DistrictInfo(
            district_data.iloc[0]['ppcstot'],
            district_data.iloc[0]['predcost'],
            district_data.iloc[0]['fundinggap'],
            district_data.iloc[0]['outcomegap'],
            district_data.iloc[0]['enroll'],
            0,
            district_data.iloc[0]['state_name']
        )
        
        district_dict = asdict(curr_district)
        return json.dumps(district_dict)
    
    def get_specific_year_data(self, type, year):
        return self.df_avg_year_data.loc[year - 2009 + 1, type]
    
    def get_year_data(self):
        funding_gap, year = [], []
        for i in range(len(self.df_avg_year_data)):
            year.append(self.df_avg_year_data.loc[i, 'year'])
            funding_gap.append(self.df_avg_year_data.loc[i, 'fundinggap'])
        
        return [funding_gap, year]
    
    def plot_district(self, name):
        funding_gap, year = [], []
        for i in self.districts[name]:
            if i.year == 0:
                continue
            funding_gap.append(i.funding_gap)
            year.append(i.year)

        print(funding_gap)
        print(year)

        fig, ax = plt.subplots()
        ax.plot(year, funding_gap, color='green', linewidth=2.0)
        avg_funding_gap, avg_year = self.get_year_data()
        ax.plot(avg_year, avg_funding_gap, color='blue', linewidth=2.0)
        ax.set_xlabel('Year')
        ax.set_ylabel('Funding Gap')
        ax.set_title(f'Funding Gap Over Years for District {name}')

        # Convert plot to PNG image
        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)
        return Response(pngImage.getvalue(), mimetype='image/png')
    
    def plot_map(self):
        postal_code = "90015" # GET FROM FRONTEND
        conn = http.client.HTTPConnection('api.positionstack.com')

        params = urllib.parse.urlencode({
            'access_key': API_KEY,
            'query': postal_code,
            'country': 'US',
            'limit': 1
            })

        conn.request('GET', '/v1/forward?{}'.format(params))

        res = conn.getresponse()
        data = res.read()

        x = data.decode('utf-8')
        json_data = json.loads(x)
        ui_lat = json_data['data'][0]["latitude"]
        ui_lon = json_data['data'][0]["longitude"]

        df = pd.read_csv(r"data/dataset_by_avgs.csv")
        avg_fundinggap = df['fundinggap'].mean()

        city_data = df['city'].tolist()
        state_data = df['state_name'].tolist()

        mapbox_access_token = open("../../mapbox_token").read()

        fig = px.scatter_mapbox(df, 
            lat="lat", 
            lon="lon", 
            color="fundinggap", 
            size="ppcstot",
            hover_name="district",  # Specify column for hover name
            hover_data={
                "<b>City</b>": df['city'],  # Make city name bold, 
            },
            color_continuous_scale=px.colors.diverging.Portland,
            color_continuous_midpoint=avg_fundinggap,
            size_max=15,
            zoom=3
        )

        fig.update_traces(marker_size=df['fundinggap'].abs())
        fig.update_layout(mapbox_center={"lat": ui_lat, "lon": ui_lon})
        # fig.write_html("plot.html")
        graphJSON = plotly.io.to_json(fig, pretty=True)
        return graphJSON

school_district_instance = SchoolDistrict()
school_district_instance.set_data()
result = school_district_instance.get_all_data()

@app.route('/api/districts', methods=['POST'])
def get_district_data():
    try:
        data = request.get_json()
        district_name = data.get('districtName', '')  # Assuming the key is 'districtName' in the request JSON
        if not district_name:
            raise ValueError("District name is missing in the request data.")

        data_response = school_district_instance.get_specific_district_data(district_name)

        return data_response

    except Exception as e:
        error_message = f"Error getting data for district: {str(e)}"
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/plot.png', methods=['POST'])
def display_graph():
    try:
        data = request.get_json()
        district_name = data.get('districtName', '')  # Assuming the key is 'districtName' in the request JSON
        if not district_name:
            raise ValueError("District name is missing in the request data.")

        image_response = school_district_instance.plot_district(district_name)

        return image_response

    except Exception as e:
        error_message = f"Error generating plot: {str(e)}"
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/map')
def display_map():
    return school_district_instance.plot_map()


if __name__ == "__main__":
    app.run(debug=True)
