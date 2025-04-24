import streamlit as st
import json
import os
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Audio Rating System", layout="wide")

# Style settings
st.markdown("""
<style>
    .header {
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    .audio-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .rating-container {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# Example mapping data - this would be loaded from a file in a real scenario
default_mapping = [
    {
        "id": "1",
        "text": "Hello, world!",
        "audios": {
            "audio_1": 4,
            "audio_2": 1,
            "audio_3": 3,
            "audio_4": 2
        }
    },
    {
        "id": "2",
        "text": "The quick brown fox jumps over the lazy dog.",
        "audios": {
            "audio_1": 4,
            "audio_2": 1,
            "audio_3": 3,
            "audio_4": 2
        }
    }
]

# Function to load mapping data from file
def load_mapping_data(file_path="mapping_data.json"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default_mapping

# Function to save results
def save_ratings(ratings, file_path="ratings_results.json"):
    # Create a timestamp for this submission
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the results
    submission = {
        "timestamp": timestamp,
        "ratings": ratings
    }
    
    # Load existing results if any
    all_results = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            all_results = json.load(f)
    
    # Add new submission
    all_results.append(submission)
    
    # Save back to file
    with open(file_path, "w") as f:
        json.dump(all_results, f, indent=4)
    
    return True

# Main app
def main():
    st.markdown('<div class="header">Audio Rating System</div>', unsafe_allow_html=True)
    
    st.write("""
    Listen to each audio sample and rate it from 1 to 5 stars.
    The audios are randomized and anonymized - you won't know which TTS model produced which audio.
    """)
    
    # Load the mapping data
    mapping_data = load_mapping_data()
    
    # Initialize session state for ratings if not already done
    if 'ratings' not in st.session_state:
        st.session_state.ratings = {item["id"]: {"text": item["text"], "audio_ratings": {}} for item in mapping_data}
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Display each text sample with its audio options
    for item in mapping_data:
        sample_id = item["id"]
        text = item["text"]
        audio_mapping = item["audios"]
        
        st.markdown(f'<div class="audio-container">', unsafe_allow_html=True)
        st.subheader(f"Sample {sample_id}")
        st.write(f"**Text:** {text}")
        
        # Display four audio players in a row
        cols = st.columns(4)
        
        for idx, (audio_key, model_id) in enumerate(audio_mapping.items()):
            with cols[idx]:
                st.write(f"**Audio {idx+1}**")
                
                # In a real app, you would have actual audio files
                # Here we just simulate with a placeholder
                # st.audio(f"path/to/audio/model_{model_id}/sample_{sample_id}.mp3")
                
                # Since we don't have real audio files, we'll just use a dummy widget
                st.markdown(f"*Audio player would be here*")
                
                # Rating for this audio
                rating_key = f"{sample_id}_{audio_key}"
                rating = st.slider(
                    f"Rate Audio {idx+1}",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=rating_key
                )
                
                # Store the rating in session state
                st.session_state.ratings[sample_id]["audio_ratings"][audio_key] = {
                    "display_position": idx+1,
                    "actual_model": model_id,
                    "rating": rating
                }
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    if st.button("Submit Ratings", type="primary", use_container_width=True):
        if save_ratings(st.session_state.ratings):
            st.session_state.submitted = True
            st.success("Your ratings have been submitted successfully!")
        else:
            st.error("There was an error saving your ratings.")
    
    # Show current ratings in JSON format (for debugging)
    if st.checkbox("Show current ratings data"):
        st.json(st.session_state.ratings)
    
    # If ratings were submitted, show a reset button
    if st.session_state.submitted:
        if st.button("Rate more samples", use_container_width=True):
            st.session_state.ratings = {item["id"]: {"text": item["text"], "audio_ratings": {}} for item in mapping_data}
            st.session_state.submitted = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()