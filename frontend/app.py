import streamlit as st
import requests
import time
import os

st.set_page_config(page_title="BrandSync", page_icon="🎬", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.title("🎬 BrandSync Ad Generator")
st.markdown("Automated Multi-Modal Video Ad Generation from a single URL.")

if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "status" not in st.session_state:
    st.session_state.status = None
if "contract" not in st.session_state:
    st.session_state.contract = None
if "final_video_url" not in st.session_state:
    st.session_state.final_video_url = None

def generate_ad(url, template):
    with st.spinner("Initializing AI Brain and Scraper..."):
        try:
            res = requests.post(f"{API_BASE_URL}/generate", json={"url": url, "template": template})
            res.raise_for_status()
            data = res.json()
            st.session_state.task_id = data["task_id"]
            st.session_state.status = data["status"]
        except Exception as e:
            st.error(f"Failed to start generation: {e}")

# Sidebar for Input
with st.sidebar:
    st.header("1. Input")
    url_input = st.text_input("Business URL", placeholder="https://www.example.com")
    template_input = st.selectbox(
        "Template / Vibe", 
        ["Default (Auto-detect)", "Energetic & Modern", "Calm & Trustworthy", "Cinematic & Epic"]
    )
    
    if st.button("Generate Ad", type="primary"):
        if url_input:
            generate_ad(url_input, template_input)
        else:
            st.warning("Please enter a URL.")

# Main area
if st.session_state.task_id:
    st.header(f"Generation Status: `{st.session_state.status}`")
    
    # Auto-polling
    if st.session_state.status not in ["completed", "failed"]:
        time.sleep(2)
        try:
            res = requests.get(f"{API_BASE_URL}/status/{st.session_state.task_id}")
            if res.status_code == 200:
                data = res.json()
                st.session_state.status = data.get("status")
                st.session_state.contract = data.get("style_contract")
                st.session_state.final_video_url = data.get("final_video_url")
                st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend server. Is FastAPI running?")
            st.stop()

    # Layout: Status and Result
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💡 Style Contract (The Brain)")
        if st.session_state.contract:
            st.json(st.session_state.contract)
        else:
            st.info("Waiting for Gemini 3 Flash to generate contract...")
            
    with col2:
        st.subheader("🎞️ Final Synthesized Ad")
        if st.session_state.status == "completed":
            st.success("Generation Complete!")
            # Fetch video endpoint with cache-buster to force reload
            video_endpoint = f"{API_BASE_URL}/video/{st.session_state.task_id}?t={time.time()}"
            st.video(video_endpoint)
        elif st.session_state.status == "failed":
            st.error("Generation failed. Please check backend logs.")
        else:
            # Show progress bar based on status
            status_map = {
                "pending_generation": 20,
                "generating": 60,
                "synthesizing": 90
            }
            progress = status_map.get(st.session_state.status, 0)
            st.progress(progress / 100.0)
            st.info("Models are working... Please wait.")
            
    st.divider()
    
    # Gemini Live Feedback Loop
    if st.session_state.status == "completed":
        st.subheader("🎙️ Gemini Live Feedback")
        st.markdown("Want to tweak the ad? Type your feedback below, and Gemini will update the style contract and trigger a partial re-regeneration.")
        
        feedback = st.text_area("Feedback (e.g. 'Make the background music more upbeat (BPM 140) and change visual style to Neon Cyberpunk')")
        
        if st.button("Update & Re-generate"):
            with st.spinner("Processing feedback..."):
                # Simplified simulation: parsing text for keywords to update contract
                # Real implementation would call Gemini here to parse the text into a JSON patch.
                patch = {}
                if "upbeat" in feedback.lower():
                    patch["audio_vibe"] = "Upbeat neon"
                    patch["audio_bpm"] = 140
                if "cyberpunk" in feedback.lower():
                    patch["visual_style"] = "Neon Cyberpunk, glowing, highly detailed"
                
                if not patch:
                    # just generic update
                    patch["visual_style"] = feedback
                    
                try:
                    res = requests.put(f"{API_BASE_URL}/feedback/{st.session_state.task_id}", json=patch)
                    if res.status_code == 200:
                        st.session_state.status = "pending_generation"
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit feedback: {e}")
