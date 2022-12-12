import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import json
import plotly.express as px
named_colorscales = list(px.colors.named_colorscales())

with open("data/tif_boundaries_id_fixed.geojson") as data:
    geo = json.load(data)


def google_sheet(sheet_url:str)->str:
  url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
  return url

# Add title and header
st.title("Chicago TIF Districts")
st.write("A PublicDataTools project by Anthony Moser")
# instructions = st.sidebar.checkbox(label="Show instructions", value=1)
# if instructions:
#     st.markdown("""
#         This is a tool for making maps of Chicago TIF data. Paste in the URL of a publicly viewable Google Sheet
#     """)

demo_url = "https://docs.google.com/spreadsheets/d/1sJVp7PlCfgfn77mAQs9gLw8Yom_50Tpbk4spWUDGp-w/edit#gid=0"

about = st.sidebar.button("About This Tool")
if about:
    st.markdown(f"This tool can visualize any Chicago TIF data as long as it's in a publicly accessible Google sheet  " 
            + " and contains a field with the TIF number. Just paste the URL here and select the field with tif_number in it.  "
            + " Make sure the numeric data doesn't have any extra formatting like commas or $ signs. Here's [an example]({demo_url})")

data_url = st.sidebar.text_input("Google Sheet URL", key="sheet_url", value=demo_url)
data_fields = []

if data_url:

    df = pd.read_csv(google_sheet(data_url)).convert_dtypes()
    ef = df.copy()
    
    fields = list(df.columns)
    metrics = [c for c in list(df.select_dtypes(['object', 'number'])) if c != "tif_number"]
    lowercase = [f.lower() for f in fields]
    
    tif_name_index = 0
    tif_number_index = 0

    for f in lowercase:
        if "tif_number" in f:
            tif_number_index = lowercase.index(f)
        if "tif_name" in f:
            tif_name_index = lowercase.index(f)
        

    # col1, col2 = st.columns(2)    
    tif_number_field = st.sidebar.selectbox(label="TIF Number field", options = fields, index = tif_number_index)
    tif_name_field = st.sidebar.selectbox(label="TIF Name field", options = fields, index = tif_name_index)
    color_scale = st.sidebar.selectbox('Color scale', options=named_colorscales, index=1)
    query = st.sidebar.text_input('Optional: Filter the data with a query', placeholder="")
    
    table = st.dataframe(ef, width=800)
      
    ef[tif_number_field] = ef[tif_number_field].astype('str')
    index_field = "tif_number"
    indexed = True
    
    selected_field = st.selectbox(label="Column to visualize:", options=metrics)

    if query:
        ef = ef.query(query)
        table.dataframe(ef)

    if indexed:
        table.dataframe(ef)
        field_name = selected_field 
        # ef['hover_text'] = ''
        ef['hover_text'] = ef[tif_name_field]

        # Geographic Map
        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=geo,
                locations=ef['tif_number'],
                featureidkey=f"properties.tif_number",
                z=ef[selected_field],
                colorscale=color_scale,
                text = ef['hover_text'],
                # zmin=1,
                # zmax=50,
                marker_opacity=0.5,
                marker_line_width=0,
            )
        )
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=10.0,
            mapbox_center={"lat":41.8223348, "lon": -87.6682938},
            width=800,
            height=800,
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)


