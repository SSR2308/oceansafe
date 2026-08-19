# 🌊 Ocean Safe

A mobile-first web app that combines real-time ocean/beach conditions, an AI safety chatbot, community hazard reporting, and fishing guidance into one platform, built to keep beachgoers safe and informed.

**Recognition:** Top 10 finalist, Congressional App Challenge — California's 47th Congressional District.

**Demo video:** [Watch the presentation](https://drive.google.com/file/d/1-xldHEz9fxrd6zQRUwMC227LTkRYFs2V/view?usp=sharing) — a walkthrough of the app and the idea behind it. A short splash clip (`bc8c-f169-4534-a82d-acc2fad66609.mp4`) is also bundled in this repo and plays on app launch.

## Pitch

> Hi everyone, thanks for meeting with me today. I'm excited to share my project, OceanSafe, which is a mobile app aimed at improving beach and ocean safety. The idea is to combine real-time data, AI insights, fishing guidance, and community reporting into one platform to keep beachgoers safe and informed.

This app is unique because it combines real-world safety, fishing guidance, and AI in one tool. It has strong community impact, especially for Southern California beaches, and it's scalable — it could eventually expand to any coastal region.

## Features

### Built in this prototype

- **Beach Safety Dashboard** — live weather (OpenWeatherMap) and NOAA tide predictions for six Southern California beaches (Santa Monica Pier, Venice Beach, Malibu Surfrider, Huntington Beach, Newport Beach, Laguna Beach), each with fun facts and visitor info (parking, hours, dog policy, amenities).
- **Interactive hazard map** — Mapbox GL map centered on the user's live location; click anywhere to drop a geotagged hazard report (jellyfish, trash, high surf, broken glass, etc.), with turn-by-turn walking directions to the selected beach.
- **Tidebot AI safety assistant** — a retrieval-augmented chatbot (LangChain + OpenAI + Pinecone) that answers beach-safety questions in plain language, grounded in a curated knowledge base rather than making things up.

### MVP vision (original pitch scope)

1. **Beach Safety Alerts** — real-time NOAA/Surfline/local-government data on tides, currents, wave height, and UV index, with push notifications for hazards like rip currents, high surf, or jellyfish season.
2. **AI Safety Assistant** — explains hazards in plain language (e.g. "red flag means strong currents; avoid swimming past waist depth") and covers first-aid basics.
3. **Community Hazard Reports** — geotagged, timestamped user reports feeding a live hazard map.
4. **Fishing Guide** — species-based CA fishing regulations, seasons, catch limits, and size requirements, linking to official CDFW resources.
5. **Beach Dashboard** — color-coded (green/yellow/red) at-a-glance safety status per beach.

### Stretch goals

- Gamification — points for submitting hazard reports.
- Augmented reality mode — point your phone at the ocean, see rip current risk overlaid live.
- AI hazard detection from photos of water/debris.
- Multilingual mode — Spanish, Vietnamese, Korean.

## Tech stack

This prototype was built as a **Python/Streamlit web app** to move fast on a working demo:

- **App framework:** Streamlit (multipage app: `home.py` + `pages/`)
- **AI chatbot:** OpenAI (`gpt-4o-mini`) + LangChain, retrieval-augmented over a Pinecone vector index
- **Data:** NOAA Tides & Currents API, OpenWeatherMap API
- **Mapping:** Mapbox GL JS (embedded via `streamlit.components.v1`), including live geolocation and walking directions
- **Deployable via GitHub Codespaces** — `.devcontainer/devcontainer.json` auto-installs dependencies and launches the app on attach

The original pitch's target stack for a production mobile app was native iOS (Swift/Xcode) with Firebase for auth/database/hosting; a natural next step once the concept, chatbot, and data integrations are validated (which is what this prototype does).

## Repository structure

```
.
├── home.py                          # Landing page + splash animation
├── rag.py                           # Tidebot's retrieval-augmented generation pipeline
├── requirements.txt
├── pages/
│   ├── 1_Beach_Dashboard.py         # Weather, tides, hazard map, directions
│   └── 2_Tidebot.py                 # AI safety chatbot UI
├── .streamlit/
│   └── secrets.toml.example         # Template for required API keys
├── .devcontainer/
│   └── devcontainer.json            # One-click Codespaces setup
└── bc8c-f169-4534-a82d-acc2fad66609.mp4   # Splash screen clip
```

## Running locally

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your own keys:
   - `OPENAI_API_KEY` — OpenAI API key for Tidebot
   - `PINECONE_API_KEY` and `INDEX_HOST` — Pinecone vector index backing Tidebot's knowledge base
   - `OPENWEATHER_API_KEY` — OpenWeatherMap API key for live weather
   - `MAPBOX_TOKEN` — Mapbox access token for the hazard map and directions
3. Run the app:
   ```
   streamlit run home.py
   ```

Or open the repo in **GitHub Codespaces** — the devcontainer installs everything and forwards port 8501 automatically (you'll still need to add your own `.streamlit/secrets.toml`).

## Future work

Building out the remaining MVP scope (push notification alerts, the fishing guide, a fully live green/yellow/red hazard rating), then the stretch goals: gamified hazard reporting, AR rip-current overlay, image-based AI hazard detection, and multilingual support; eventually migrating the validated concept to a native iOS app on Firebase, as originally scoped.

## Author

Shravan Suresh
