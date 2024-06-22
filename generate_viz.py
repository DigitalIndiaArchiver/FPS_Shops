import pandas as pd
import geopandas as gpd
import folium
import datapane as dp
import matplotlib.pyplot as plt

# Load the consolidated FPS data
df = pd.read_csv('ConsolidatedShops.csv')

# Ensure categorical columns are treated as such
df['stateName'] = df['stateName'].astype('category')
df['districtName'] = df['districtName'].astype('category')
df['tehsilName'] = df['tehsilName'].astype('category')
df['villageName'] = df['villageName'].astype('category')

# Create visualizations

# 1. Distribution of FPS by State
state_dist = df['stateName'].value_counts().plot(kind='bar', title='Distribution of FPS by State').get_figure()
state_dist.savefig('./datapane_report/state_distribution.png')
plt.clf()

# 2. Distribution of FPS by District
district_dist = df['districtName'].value_counts().head(20).plot(kind='bar', title='Top 20 Districts by Number of FPS').get_figure()
district_dist.savefig('./datapane_report/district_distribution.png')
plt.clf()

# 3. Distribution of FPS by Tehsil
tehsil_dist = df['tehsilName'].value_counts().head(20).plot(kind='bar', title='Top 20 Tehsils by Number of FPS').get_figure()
tehsil_dist.savefig('./datapane_report/tehsil_distribution.png')
plt.clf()

# 4. Create a map visualization
# Load a GeoJSON file with the boundaries of Indian states
india_geojson_url = 'https://github.com/datta07/INDIAN-SHAPEFILES/raw/master/INDIA/INDIA_STATES.geojson'
india_states = gpd.read_file(india_geojson_url)

# Group data by state and get the count of FPS per state
state_counts = df['stateName'].value_counts().reset_index()
state_counts.columns = ['stateName', 'fpsCount']

# Merge state counts with the GeoDataFrame
india_states = india_states.merge(state_counts, how='left', left_on='STNAME', right_on='stateName')

# Create a Folium map centered around India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Add state boundaries to the map
folium.Choropleth(
    geo_data=india_states,
    name='choropleth',
    data=india_states,
    columns=['stateName', 'fpsCount'],
    key_on='feature.properties.STNAME',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Number of FPS Shops'
).add_to(m)

# Save the map as an HTML file
map_file = './datapane_report/india_fps_map.html'
m.save(map_file)

# Function to search FPS by village name
def search_fps_by_village(village_name):
    return df[df['villageName'] == village_name]

# Prepare Datapane report
report = dp.Report(
    dp.Page(
        title="Overview",
        blocks=[
            dp.Text("# India PDS Tracker -- FPS Shops Data Overview"),
            dp.Text("This report provides an overview of the Fair Price Shops (FPS) distribution across different states, districts, and tehsils in India."),
        ]
    ),
    dp.Page(
        title="State Distribution",
        blocks=[
            dp.Text("## Distribution of FPS by State"),
            dp.Media(file='datapane_report/state_distribution.png'),
            dp.DataTable(df[['stateName', 'fpsCode']].groupby('stateName').count().reset_index().rename(columns={'fpsCode': 'Number of FPS'}))
        ]
    ),
    dp.Page(
        title="District Distribution",
        blocks=[
            dp.Text("## Top 20 Districts by Number of FPS"),
            dp.Media(file='datapane_report/district_distribution.png'),
            dp.DataTable(df['districtName'].value_counts().head(20).reset_index().rename(columns={'index': 'District', 'districtName': 'Number of FPS'}))
        ]
    ),
    dp.Page(
        title="Tehsil Distribution",
        blocks=[
            dp.Text("## Top 20 Tehsils by Number of FPS"),
            dp.Media(file='datapane_report/tehsil_distribution.png'),
            dp.DataTable(df['tehsilName'].value_counts().head(20).reset_index().rename(columns={'index': 'Tehsil', 'tehsilName': 'Number of FPS'}))
        ]
    )
)

# Save the report
report.save(path='./datapane_report/fps_shops_report.html', open=True)
