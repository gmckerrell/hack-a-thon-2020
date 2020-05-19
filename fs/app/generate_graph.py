#generate graphs
#p1 = csv file input
#p2 = x-axis
#p3 = y-axis

# covidesafe.com,2020-05-10,    US,     ns75.domaincontrol.com, 2,  1,  337,    66
# domain        ,registereddate,country,DNS host,               vt, q9, shannon,levenshtein

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import csv, country_codes
import os, sys, datetime
from collections import OrderedDict

#date/number
#1) count date
#2) plt cound for each date x=date, count = y
def plot_number_per_date(data, fig):
    dates = {}
    for node in data:
        if node.registereddate not in dates.keys():
            dates[node.registereddate] = 1
        else: 
            dates[node.registereddate] += 1
    
    dates2 = OrderedDict(sorted(dates.items()))
    fig.add_trace(go.Scatter(x=list(dates2.keys()), y=list(dates2.values()), mode='lines'))

def plot_map(data, fig):
    data_locations = {}
    unknown = 0
    
    for node in data:
        try:
            country = country_codes.codes()[node.country]
            if str(country) not in data_locations.keys():
                data_locations[str(country)] = 1
            else:
                data_locations[str(country)] += 1
        except:
            unknown += 1
            
    fig.add_trace(go.Choropleth(locationmode="country names",
        locations=list(data_locations.keys()),
        z = list(data_locations.values()),
        colorscale="reds",
        colorbar = {"len":0.5, "y":0, "yanchor":"bottom"}))

def import_csv(csv_path):
    data = []
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        headers = csv_reader.next() # skip the headers
        for domain, registereddate, country, DNShost, vt, q9, shannon, levenshtein in csv_reader:
            data.append(Graph_node(domain, registereddate, country, DNShost, vt, q9, shannon, levenshtein))
    return data

class Graph_node:
        def __init__(self, domain, registereddate, country, DNShost, vt, q9, shannon, levenshtein):
            global n_homeless
            if (country == '?'):
                n_homeless+=1
            self.domain = domain
            self.registereddate = datetime.datetime.strptime(registereddate,'%Y-%m-%d').isoformat()
            self.country = country
            self.DNShost = DNShost
            self.vt = vt
            self.q9 = q9
            self.shannon = shannon
            self.levenshtein = levenshtein
    
(csv_file, output_dir, search) = sys.argv[1:]

n_homeless=0
data = import_csv(csv_file)
n_total=len(data)
fig = make_subplots(
    rows=2, cols=1,
    specs=[[{"type": "xy"}], [{"type":"choropleth"}]],
    subplot_titles=(
        "Number of New Domains Matching '%s' Over Time"%search,
        "Location of Domain Names Matching '%s' Word<br>(no identified location for %d of %d)"%(search,n_homeless,n_total),
    ),
)

plot_number_per_date(data, fig)
plot_map(data, fig)

fig.write_html(
    os.path.join(output_dir,"index.html")
)
