import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
import streamlit.components.v1 as components

# ---------------------------
# API Keys from Secrets
# ---------------------------
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]

# ---------------------------
# Weather Data
# ---------------------------
def get_weather_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=imperial"
    res = requests.get(url)
    data = res.json()
    return {
        "Temperature (°F)": round(data["main"]["temp"], 2),
        "Weather": data["weather"][0]["description"].title(),
        "UV Index": "Check local UV forecast"
    }

# ---------------------------
# Tide Data
# ---------------------------
def get_tide_data(station_id="9410840"):
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "station": station_id,
        "product": "predictions",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "h",
        "format": "json",
        "date": "today"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if "predictions" in data:
            df = pd.DataFrame(data['predictions'])
            df['t'] = pd.to_datetime(df['t'])
            df.rename(columns={'v': 'Tide (ft)'}, inplace=True)
            df['Tide (ft)'] = pd.to_numeric(df['Tide (ft)'], errors='coerce').round(2)
            return df
        else:
            st.warning(f"⚠ NOAA API returned no predictions for station {station_id}.")
            return pd.DataFrame(columns=['t', 'Tide (ft)'])
    except Exception as e:
        st.error(f"Failed to fetch tide data: {e}")
        return pd.DataFrame(columns=['t', 'Tide (ft)'])

# ---------------------------
# Tide Summary
# ---------------------------
def summarize_tides(tide_df):
    if tide_df.empty:
        return pd.DataFrame()

    df = tide_df.copy()
    df['diff'] = df['Tide (ft)'].diff().fillna(0)

    high_tides = df[(df['diff'] > 0) & (df['diff'].shift(-1) < 0)]
    low_tides = df[(df['diff'] < 0) & (df['diff'].shift(-1) > 0)]

    summary = pd.concat([
        pd.DataFrame({
            "Time": high_tides['t'],
            "Tide (ft)": high_tides['Tide (ft)'],
            "Type": "High Tide"
        }),
        pd.DataFrame({
            "Time": low_tides['t'],
            "Tide (ft)": low_tides['Tide (ft)'],
            "Type": "Low Tide"
        })
    ]).sort_values("Time")

    summary['Time'] = summary['Time'].dt.strftime("%I:%M %p")
    summary['Tide (ft)'] = summary['Tide (ft)'].round(2)
    return summary

# ---------------------------
# Beach Data
# ---------------------------
beaches = {
    "Santa Monica Pier": {
        "lat": 34.0100, "lon": -118.4950, "station": "9410840",
        "image": "https://images.squarespace-cdn.com/content/v1/5e0e65adcd39ed279a0402fd/1627422658456-7QKPXTNQ34W2OMBTESCJ/1.jpg?format=2500w",
        "description": "An iconic landmark offering stunning ocean views, amusement rides, and family-friendly attractions.",
        "fun_facts": [
            "Opened in 1909.",
            "Home to Pacific Park, the only amusement park on a California pier.",
            "Featured in many films and TV shows."
        ],
        "visitor_info": {
            "Dogs Allowed": "No",
            "Parking": "Paid; free 8 PM–6 AM",
            "Beach Hours": "6 AM – 10 PM",
            "Nearby Amenities": "Restrooms, Food, Lifeguard Station"
        }
    },
    "Venice Beach": {
        "lat": 33.9850, "lon": -118.4695, "station": "9410840",
        "image": "https://drupal-prod.visitcalifornia.com/sites/default/files/styles/fluid_1920/public/VC_California101_VeniceBeach_Stock_RF_638340372_1280x640.jpg.webp?itok=emtWYsp9",
        "description": "Known for its bohemian spirit, street performers, and bustling boardwalk.",
        "fun_facts": [
            "Home to Muscle Beach outdoor gym.",
            "Venice Canals inspired by Venice, Italy.",
            "Popular filming location for music videos."
        ],
        "visitor_info": {
            "Dogs Allowed": "Yes, on leash",
            "Parking": "Paid; free before 8 AM",
            "Beach Hours": "6 AM – 10 PM",
            "Nearby Amenities": "Skate Park, Food, Restrooms"
        }
    },
    "Malibu Surfrider Beach": {
        "lat": 34.0360, "lon": -118.6880, "station": "9410840",
        "image": "https://www.worldbeachguide.com/photos/large/malibu-beach-pier-lagoon.jpg",
        "description": "Famous for perfect waves and surf culture.",
        "fun_facts": [
            "Known as 'The First Point' by surfers.",
            "Part of Malibu Lagoon State Beach.",
            "Hosts surf competitions."
        ],
        "visitor_info": {
            "Dogs Allowed": "No",
            "Parking": "Free parking lot, first-come-first-serve",
            "Beach Hours": "Sunrise to Sunset",
            "Nearby Amenities": "Lifeguard Station, Restrooms"
        }
    },
    "Huntington Beach": {
        "lat": 33.6595, "lon": -117.9988, "station": "9411270",
        "image": "https://www.redfin.com/blog/wp-content/uploads/2023/12/GettyImages-1812336731.jpg",
        "description": "Also known as Surf City USA, world-famous for surfing.",
        "fun_facts": [
            "Hosts the US Open of Surfing.",
            "Pier extends 1,850 feet into the ocean.",
            "Great for volleyball and beach events."
        ],
        "visitor_info": {
            "Dogs Allowed": "No",
            "Parking": "Paid, free 8 PM–6 AM",
            "Beach Hours": "6 AM – 10 PM",
            "Nearby Amenities": "Lifeguard Station, Food, Restrooms"
        }
    },
    "Newport Beach": {
        "lat": 33.6189, "lon": -117.9290, "station": "9411340",
        "image": "https://static.independent.co.uk/2023/07/27/12/iStock-1210240213%20%281%29.jpg",
        "description": "Offers wide sandy beaches and a bustling harbor.",
        "fun_facts": [
            "Famous for Newport Harbor boating.",
            "Home to Balboa Fun Zone amusement area.",
            "Popular for whale watching."
        ],
        "visitor_info": {
            "Dogs Allowed": "Yes, on leash",
            "Parking": "Paid parking",
            "Beach Hours": "6 AM – 10 PM",
            "Nearby Amenities": "Lifeguard Station, Food, Restrooms"
        }
    },
    "Laguna Beach": {
        "lat": 33.5427, "lon": -117.7854, "station": "9411340",
        "image": "https://cdn.britannica.com/37/189937-050-478BECD3/Night-view-Laguna-Beach-California.jpg",
        "description": "Known for art galleries, tide pools, and dramatic cliffs.",
        "fun_facts": [
            "Home to the annual Pageant of the Masters.",
            "Famous for tide pools and snorkeling.",
            "Coastal cliffs provide scenic viewpoints."
        ],
        "visitor_info": {
            "Dogs Allowed": "Yes, on leash",
            "Parking": "Paid parking",
            "Beach Hours": "6 AM – 10 PM",
            "Nearby Amenities": "Restrooms, Food, Lifeguard Station"
        }
    }
}

# ---------------------------
# Streamlit Page Setup
# ---------------------------
st.title("🌊 California Beach Safety Dashboard")

if "hazard_reports" not in st.session_state:
    st.session_state["hazard_reports"] = []

# ---------------------------
# Beach Selection
# ---------------------------
selected_beach = st.selectbox("Select Beach:", list(beaches.keys()))
beach_coords = beaches[selected_beach]

# ---------------------------
# Beach Image and Description
# ---------------------------
st.image(beach_coords["image"], use_column_width=True, caption=selected_beach)
st.subheader(f"About {selected_beach}")
st.write(beach_coords["description"])

with st.expander("🌟 Fun Facts"):
    for fact in beach_coords["fun_facts"]:
        st.markdown(f"- {fact}")

with st.expander("📍 Visitor Information"):
    for key, value in beach_coords["visitor_info"].items():
        st.markdown(f"**{key}:** {value}")

# ---------------------------
# Weather Metrics
# ---------------------------
st.subheader(f"🏖️ {selected_beach} Overview")
weather = get_weather_data(beach_coords["lat"], beach_coords["lon"])
cols = st.columns(3)
cols[0].metric("🌡 Temperature", f"{weather['Temperature (°F)']} °F")
cols[1].metric("☀ Weather", weather["Weather"])
cols[2].metric("🕶 UV Index", weather["UV Index"])

# ---------------------------
# Tide Summary and Chart
# ---------------------------
st.subheader("🌊 Tide Forecast (Next 24 Hours)")
tide_df = get_tide_data(beach_coords["station"])

if not tide_df.empty:
    tide_summary = summarize_tides(tide_df)
    
    if not tide_summary.empty:
        st.markdown("**🕒 Upcoming High and Low Tides**")
        st.table(tide_summary)
    else:
        st.info("No high/low tide points found for today.")
    
    tide_df['Tide (ft)'] = tide_df['Tide (ft)'].round(2)
    
    with st.expander("📈 Show Tide Graph"):
        fig = px.line(
            tide_df.head(24),
            x='t',
            y='Tide (ft)',
            title="Tide Levels - Next 24 Hours",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Tide Height (ft)",
            xaxis_tickformat="%I:%M %p",
            template="plotly_white",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No tide data available for this beach.")

# ---------------------------
# Hazard Reporting Section
# ---------------------------
st.subheader("📢 Report a Hazard")
st.markdown(
    "Click anywhere on the map to report a hazard directly. "
    "You can enter types like Jellyfish, Broken glass, High surf, or Trash."
)

# ---------------------------
# Map Section
# ---------------------------
# ---------------------------
# Map Section
# ---------------------------
hazard_data_json = json.dumps(st.session_state["hazard_reports"])
show_directions = st.checkbox("Direction to Beach from Current Location", key="directions_toggle")

components.html(f"""
<head>
<link href='https://api.mapbox.com/mapbox-gl-js/v1.12.0/mapbox-gl.css' rel='stylesheet' />
<script src='https://api.mapbox.com/mapbox-gl-js/v1.12.0/mapbox-gl.js'></script>
<script src='https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-directions/v4.1.0/mapbox-gl-directions.js'></script>
<link rel='stylesheet' href='https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-directions/v4.1.0/mapbox-gl-directions.css' />
</head>
<body>
<div id='map' style='width:100%; height:650px;'></div>
<script>
mapboxgl.accessToken = '{MAPBOX_TOKEN}';

// helper to compute bounds from an array of [lng,lat] coords
function coordsToBounds(coords){{
    if(!coords || coords.length === 0) return null;
    var minLng = coords[0][0], minLat = coords[0][1], maxLng = coords[0][0], maxLat = coords[0][1];
    for(var i=1;i<coords.length;i++){{
        var c = coords[i];
        if(c[0] < minLng) minLng = c[0];
        if(c[0] > maxLng) maxLng = c[0];
        if(c[1] < minLat) minLat = c[1];
        if(c[1] > maxLat) maxLat = c[1];
    }}
    return [[minLng, minLat], [maxLng, maxLat]];
}}

// request location and initialize map with it (falls back to beach coords)
navigator.geolocation.getCurrentPosition(successLocation, errorLocation, {{ enableHighAccuracy: true, timeout: 10000 }});

function successLocation(position) {{
    const userCenter = [position.coords.longitude, position.coords.latitude];
    setupMap(userCenter, true);
}}

function errorLocation() {{
    setupMap([{beach_coords['lon']}, {beach_coords['lat']}], false);
}}

function setupMap(initialCenter, hasGeolocation) {{
    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: initialCenter,
        zoom: 14
    }});

    const nav = new mapboxgl.NavigationControl();
    map.addControl(nav);

    // user marker (blue)
    const userMarker = new mapboxgl.Marker({{ color: 'blue' }})
        .setLngLat(initialCenter)
        .addTo(map);

    // Add hazard markers from Python session_state
    const hazards = {hazard_data_json};
    hazards.forEach(h => {{
        if (h.beach == "{selected_beach}") {{
            new mapboxgl.Marker({{ color: 'orange' }})
            .setLngLat([h.lon, h.lat])
            .setPopup(new mapboxgl.Popup().setText(h.hazard))
            .addTo(map);
        }}
    }});

    // update user marker live, update directions origin if directions are active
    navigator.geolocation.watchPosition(function(pos) {{
        const lon = pos.coords.longitude;
        const lat = pos.coords.latitude;
        userMarker.setLngLat([lon, lat]);
        if (window.directionsInstance && typeof window.directionsInstance.setOrigin === 'function') {{
            try {{ window.directionsInstance.setOrigin([lon, lat]); }} catch(e){{ console.warn("directions setOrigin error", e); }}
        }}
    }}, function(err){{ console.error("watchPosition error", err); }}, {{ enableHighAccuracy:true }});

    // clicking map to report hazards (creates marker and posts back)
    map.on('click', function(e) {{
        const lat = e.lngLat.lat;
        const lon = e.lngLat.lng;
        const hazard = prompt("Enter hazard type (e.g., Jellyfish, Trash, High surf):");
        if(hazard) {{
            fetch("", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{lat:lat, lon:lon, hazard: hazard, beach: "{selected_beach}"}})
            }});
            new mapboxgl.Marker({{color:'orange'}})
            .setLngLat([lon, lat])
            .setPopup(new mapboxgl.Popup().setText(hazard))
            .addTo(map);
        }}
    }});

    // If "Show Directions" checked, add directions control
    if ({str(show_directions).lower()}) {{
        window.directionsInstance = new MapboxDirections({{
            accessToken: mapboxgl.accessToken,
            unit: 'imperial',
            profile: 'mapbox/walking',
            interactive: true,
            controls: {{ inputs: true, instructions: true, profileSwitcher: true }},
            fitBounds: false
        }});
        map.addControl(window.directionsInstance, 'top-left');
        try {{
            window.directionsInstance.setOrigin(initialCenter);
            window.directionsInstance.setDestination([{beach_coords['lon']}, {beach_coords['lat']}]);
        }} catch(e) {{ console.warn("initial setOrigin/setDestination error", e); }}

        let hasFittedRoute = false;
        if (window.directionsInstance && typeof window.directionsInstance.on === 'function') {{
            window.directionsInstance.on('route', function(e) {{
                if (!e || !e.route || e.route.length === 0) return;
                const route = e.route[0];
                let coords = [];
                if (route.geometry && route.geometry.coordinates) coords = route.geometry.coordinates;
                else if (route.geometry && route.geometry.type === 'LineString' && route.geometry.coordinates) coords = route.geometry.coordinates;
                else if (route.legs) {{
                    route.legs.forEach(leg => {{
                        if (leg.steps) {{
                            leg.steps.forEach(step => {{
                                if (step.geometry && step.geometry.coordinates) coords = coords.concat(step.geometry.coordinates);
                            }});
                        }}
                    }});
                }}
                if (!coords || coords.length === 0) {{
                    if (Array.isArray(route.geometry)) coords = route.geometry;
                }}
                if (coords && coords.length > 0) {{
                    const bounds = coordsToBounds(coords);
                    if (bounds) {{ map.fitBounds(bounds, {{ padding: 60, linear: true }}); hasFittedRoute = true; }}
                }} else {{
                    try {{
                        const origin = window.directionsInstance.getOrigin();
                        const destination = window.directionsInstance.getDestination();
                        if(origin && destination){{
                            const o = origin.geometry && origin.geometry.coordinates ? origin.geometry.coordinates : origin;
                            const d = destination.geometry && destination.geometry.coordinates ? destination.geometry.coordinates : destination;
                            map.fitBounds([[Math.min(o[0], d[0]), Math.min(o[1], d[1])], [Math.max(o[0], d[0]), Math.max(o[1], d[1])]], {{ padding:60 }});
                        }}
                    }} catch(err){{ console.warn("fallback fitBounds error", err); }}
                }}
            }});
        }}
    }}
}}
</script>
</body>
""", height=650)
st.write("🟢 Your location updates live (blue marker). Click the map to report hazards. If 'Show Directions' is toggled on, a route from your current location → selected beach will appear and the map will fit the entire route (instead of centering only on the beach).")
