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
import requests

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
    
    def get_specific_district_lat_lon(self, name):
        district_data = self.df_avg_data[self.df_avg_data['district'] == name]
        lat = district_data.iloc[0]['lat']
        lon = district_data.iloc[0]['lon']
        return (lat, lon)
    
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
        px.set_mapbox_access_token(open(".mapbox_token").read())
        df = pd.read_csv("./data/dataset_by_avgs.csv")
        avg_fundinggap = df['fundinggap'].mean()
        fig = px.scatter_mapbox(df, lat="lat", lon="lon",     color="fundinggap", size="ppcstot",
                        color_continuous_scale=px.colors.diverging.Portland, 
                        color_continuous_midpoint=avg_fundinggap,
                        size_max=10, zoom=2)
        
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

@app.route('/data')
def fetch_data ():
    domain = 'dev-dx8vibsd7h01hmai.us.auth0.com'
    api_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImczRUtodnRlMEp6a3RIR3N2MUx2MCJ9.eyJpc3MiOiJodHRwczovL2Rldi1keDh2aWJzZDdoMDFobWFpLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJkUGlvSHdKbUNDZXVRQ2FqWmJYMzVtT1JOMjJXUTFlbUBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtZHg4dmlic2Q3aDAxaG1haS51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTcwODg0OTQ2MCwiZXhwIjoxNzA4OTM1ODYwLCJhenAiOiJkUGlvSHdKbUNDZXVRQ2FqWmJYMzVtT1JOMjJXUTFlbSIsInNjb3BlIjoicmVhZDpjbGllbnRfZ3JhbnRzIGNyZWF0ZTpjbGllbnRfZ3JhbnRzIGRlbGV0ZTpjbGllbnRfZ3JhbnRzIHVwZGF0ZTpjbGllbnRfZ3JhbnRzIHJlYWQ6dXNlcnMgdXBkYXRlOnVzZXJzIGRlbGV0ZTp1c2VycyBjcmVhdGU6dXNlcnMgcmVhZDp1c2Vyc19hcHBfbWV0YWRhdGEgdXBkYXRlOnVzZXJzX2FwcF9tZXRhZGF0YSBkZWxldGU6dXNlcnNfYXBwX21ldGFkYXRhIGNyZWF0ZTp1c2Vyc19hcHBfbWV0YWRhdGEgcmVhZDp1c2VyX2N1c3RvbV9ibG9ja3MgY3JlYXRlOnVzZXJfY3VzdG9tX2Jsb2NrcyBkZWxldGU6dXNlcl9jdXN0b21fYmxvY2tzIGNyZWF0ZTp1c2VyX3RpY2tldHMgcmVhZDpjbGllbnRzIHVwZGF0ZTpjbGllbnRzIGRlbGV0ZTpjbGllbnRzIGNyZWF0ZTpjbGllbnRzIHJlYWQ6Y2xpZW50X2tleXMgdXBkYXRlOmNsaWVudF9rZXlzIGRlbGV0ZTpjbGllbnRfa2V5cyBjcmVhdGU6Y2xpZW50X2tleXMgcmVhZDpjb25uZWN0aW9ucyB1cGRhdGU6Y29ubmVjdGlvbnMgZGVsZXRlOmNvbm5lY3Rpb25zIGNyZWF0ZTpjb25uZWN0aW9ucyByZWFkOnJlc291cmNlX3NlcnZlcnMgdXBkYXRlOnJlc291cmNlX3NlcnZlcnMgZGVsZXRlOnJlc291cmNlX3NlcnZlcnMgY3JlYXRlOnJlc291cmNlX3NlcnZlcnMgcmVhZDpkZXZpY2VfY3JlZGVudGlhbHMgdXBkYXRlOmRldmljZV9jcmVkZW50aWFscyBkZWxldGU6ZGV2aWNlX2NyZWRlbnRpYWxzIGNyZWF0ZTpkZXZpY2VfY3JlZGVudGlhbHMgcmVhZDpydWxlcyB1cGRhdGU6cnVsZXMgZGVsZXRlOnJ1bGVzIGNyZWF0ZTpydWxlcyByZWFkOnJ1bGVzX2NvbmZpZ3MgdXBkYXRlOnJ1bGVzX2NvbmZpZ3MgZGVsZXRlOnJ1bGVzX2NvbmZpZ3MgcmVhZDpob29rcyB1cGRhdGU6aG9va3MgZGVsZXRlOmhvb2tzIGNyZWF0ZTpob29rcyByZWFkOmFjdGlvbnMgdXBkYXRlOmFjdGlvbnMgZGVsZXRlOmFjdGlvbnMgY3JlYXRlOmFjdGlvbnMgcmVhZDplbWFpbF9wcm92aWRlciB1cGRhdGU6ZW1haWxfcHJvdmlkZXIgZGVsZXRlOmVtYWlsX3Byb3ZpZGVyIGNyZWF0ZTplbWFpbF9wcm92aWRlciBibGFja2xpc3Q6dG9rZW5zIHJlYWQ6c3RhdHMgcmVhZDppbnNpZ2h0cyByZWFkOnRlbmFudF9zZXR0aW5ncyB1cGRhdGU6dGVuYW50X3NldHRpbmdzIHJlYWQ6bG9ncyByZWFkOmxvZ3NfdXNlcnMgcmVhZDpzaGllbGRzIGNyZWF0ZTpzaGllbGRzIHVwZGF0ZTpzaGllbGRzIGRlbGV0ZTpzaGllbGRzIHJlYWQ6YW5vbWFseV9ibG9ja3MgZGVsZXRlOmFub21hbHlfYmxvY2tzIHVwZGF0ZTp0cmlnZ2VycyByZWFkOnRyaWdnZXJzIHJlYWQ6Z3JhbnRzIGRlbGV0ZTpncmFudHMgcmVhZDpndWFyZGlhbl9mYWN0b3JzIHVwZGF0ZTpndWFyZGlhbl9mYWN0b3JzIHJlYWQ6Z3VhcmRpYW5fZW5yb2xsbWVudHMgZGVsZXRlOmd1YXJkaWFuX2Vucm9sbG1lbnRzIGNyZWF0ZTpndWFyZGlhbl9lbnJvbGxtZW50X3RpY2tldHMgcmVhZDp1c2VyX2lkcF90b2tlbnMgY3JlYXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgZGVsZXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgcmVhZDpjdXN0b21fZG9tYWlucyBkZWxldGU6Y3VzdG9tX2RvbWFpbnMgY3JlYXRlOmN1c3RvbV9kb21haW5zIHVwZGF0ZTpjdXN0b21fZG9tYWlucyByZWFkOmVtYWlsX3RlbXBsYXRlcyBjcmVhdGU6ZW1haWxfdGVtcGxhdGVzIHVwZGF0ZTplbWFpbF90ZW1wbGF0ZXMgcmVhZDptZmFfcG9saWNpZXMgdXBkYXRlOm1mYV9wb2xpY2llcyByZWFkOnJvbGVzIGNyZWF0ZTpyb2xlcyBkZWxldGU6cm9sZXMgdXBkYXRlOnJvbGVzIHJlYWQ6cHJvbXB0cyB1cGRhdGU6cHJvbXB0cyByZWFkOmJyYW5kaW5nIHVwZGF0ZTpicmFuZGluZyBkZWxldGU6YnJhbmRpbmcgcmVhZDpsb2dfc3RyZWFtcyBjcmVhdGU6bG9nX3N0cmVhbXMgZGVsZXRlOmxvZ19zdHJlYW1zIHVwZGF0ZTpsb2dfc3RyZWFtcyBjcmVhdGU6c2lnbmluZ19rZXlzIHJlYWQ6c2lnbmluZ19rZXlzIHVwZGF0ZTpzaWduaW5nX2tleXMgcmVhZDpsaW1pdHMgdXBkYXRlOmxpbWl0cyBjcmVhdGU6cm9sZV9tZW1iZXJzIHJlYWQ6cm9sZV9tZW1iZXJzIGRlbGV0ZTpyb2xlX21lbWJlcnMgcmVhZDplbnRpdGxlbWVudHMgcmVhZDphdHRhY2tfcHJvdGVjdGlvbiB1cGRhdGU6YXR0YWNrX3Byb3RlY3Rpb24gcmVhZDpvcmdhbml6YXRpb25zX3N1bW1hcnkgY3JlYXRlOmF1dGhlbnRpY2F0aW9uX21ldGhvZHMgcmVhZDphdXRoZW50aWNhdGlvbl9tZXRob2RzIHVwZGF0ZTphdXRoZW50aWNhdGlvbl9tZXRob2RzIGRlbGV0ZTphdXRoZW50aWNhdGlvbl9tZXRob2RzIHJlYWQ6b3JnYW5pemF0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9ucyBkZWxldGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9uX21lbWJlcnMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVycyBkZWxldGU6b3JnYW5pemF0aW9uX21lbWJlcnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyByZWFkOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9uX2Nvbm5lY3Rpb25zIGRlbGV0ZTpvcmdhbml6YXRpb25fY29ubmVjdGlvbnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9tZW1iZXJfcm9sZXMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGRlbGV0ZTpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGNyZWF0ZTpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgcmVhZDpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgZGVsZXRlOm9yZ2FuaXphdGlvbl9pbnZpdGF0aW9ucyBkZWxldGU6cGhvbmVfcHJvdmlkZXJzIGNyZWF0ZTpwaG9uZV9wcm92aWRlcnMgcmVhZDpwaG9uZV9wcm92aWRlcnMgdXBkYXRlOnBob25lX3Byb3ZpZGVycyBkZWxldGU6cGhvbmVfdGVtcGxhdGVzIGNyZWF0ZTpwaG9uZV90ZW1wbGF0ZXMgcmVhZDpwaG9uZV90ZW1wbGF0ZXMgdXBkYXRlOnBob25lX3RlbXBsYXRlcyBjcmVhdGU6ZW5jcnlwdGlvbl9rZXlzIHJlYWQ6ZW5jcnlwdGlvbl9rZXlzIHVwZGF0ZTplbmNyeXB0aW9uX2tleXMgZGVsZXRlOmVuY3J5cHRpb25fa2V5cyByZWFkOnNlc3Npb25zIGRlbGV0ZTpzZXNzaW9ucyByZWFkOnJlZnJlc2hfdG9rZW5zIGRlbGV0ZTpyZWZyZXNoX3Rva2VucyByZWFkOmNsaWVudF9jcmVkZW50aWFscyBjcmVhdGU6Y2xpZW50X2NyZWRlbnRpYWxzIHVwZGF0ZTpjbGllbnRfY3JlZGVudGlhbHMgZGVsZXRlOmNsaWVudF9jcmVkZW50aWFscyIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.u7ZWd7j7LvfDGxZkUH-tt8K46TlW1CZdRppoIznbmvrQgf5MURUOKp9KCEJioezREaWY7Be2AQ2Z_LtbpDvnYpKfd6-Hg54ZPRGzBFtSDPdOqrdpSzABpForxIWm0jusuQ0DpPafHJ0U55bikEzWV0rE6h-RXw-Cpdjg88uz7MMB7e4PjWoSkjkkaw976QKqTvYHR8oETd53rpfrgaKKmoYwdc8wr9TnkeikNYLqIqr4pSFM6mx44qYybhhZpZ8wQd2tYuDvTbHv7KgldjDXhE0hJClEVA6oUtqszFoYczCX426WUpc3CbL32XA66fHizEAMdwFLQzUF9X2WExI37A'

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    # Example: Fetch all users with pagination
    url = f'https://{domain}/api/v2/users'
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code == 200:
        users = response.json()
        return users
    else:
        print('Error fetching users:', response.text)

    
if __name__ == "__main__":
    app.run(debug=True)
