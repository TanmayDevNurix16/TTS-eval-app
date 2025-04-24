import streamlit as st
import json
import os
import random
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="TTS Model Rating System", layout="wide")

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
    .model-info {
        font-size: 12px;
        color: #666;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Function to load metadata and select random samples
def load_metadata(file_path="new_metadata.json", num_samples=10):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            all_data = json.load(f)
            # Select random samples if we have more than requested
            if len(all_data) > num_samples:
                return random.sample(all_data, num_samples)
            return all_data
    else:
        st.error(f"Metadata file not found at {file_path}")
        return []

# Model name mapping for reference (not shown to users during testing)
MODEL_NAMES = {
    1: "AWS Polly",
    2: "Google TTS",
    3: "ElevenLabs TTS",
    4: "Azure TTS"
}

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
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    return True

# Function to handle rating changes
def update_rating(sample_id, audio_key, model_id, position):
    key = f"{sample_id}_{audio_key}"
    rating = st.session_state[key]
    
    # Make sure sample_id exists in ratings dictionary
    if sample_id not in st.session_state.ratings:
        st.session_state.ratings[sample_id] = {"audio_ratings": {}}
    
    # Make sure audio_ratings exists for this sample
    if "audio_ratings" not in st.session_state.ratings[sample_id]:
        st.session_state.ratings[sample_id]["audio_ratings"] = {}
    
    # Store the rating
    st.session_state.ratings[sample_id]["audio_ratings"][audio_key] = {
        "display_position": position,
        "actual_model": model_id,
        "model_name": MODEL_NAMES.get(model_id, "Unknown"),
        "rating": rating
    }

# Main app
def main():
    st.markdown('<div class="header">TTS Model Rating System</div>', unsafe_allow_html=True)
    
    st.write("""
    Listen to each audio sample and rate it from 1 to 5 stars.
    The audios are randomized and anonymized - you won't know which TTS model produced which audio.
    """)
    
    # Load 10 random samples from metadata
    if 'samples' not in st.session_state or st.session_state.get('reload_samples', False):
        st.session_state.samples = load_metadata(num_samples=10)
        st.session_state.reload_samples = False
    
    samples = st.session_state.samples
    
    if not samples:
        st.error("No samples were loaded. Please check your metadata.json file.")
        return
    
    # Initialize session state for ratings if not already done
    if 'ratings' not in st.session_state:
        st.session_state.ratings = {}
        for item in samples:
            sample_id = str(item["id"])  # Convert to string to ensure consistent key type
            st.session_state.ratings[sample_id] = {"text": item["text"], "audio_ratings": {}}
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Show progress
    progress_text = st.empty()
    
    # Display each text sample with its audio options
    for i, item in enumerate(samples):
        sample_id = str(item["id"])  # Convert to string for consistency
        text = item["text"]
        
        # Get the correct audio mapping key (audios_1, audios_2, etc.)
        audio_key = f"audios_{sample_id}"
        if audio_key not in item:
            # Try alternate format if the key doesn't exist
            audio_key = f"audios_{int(sample_id)}"
            if audio_key not in item:
                st.warning(f"Could not find audio mapping for sample {sample_id}")
                continue
        
        audio_mapping = item[audio_key]
        
        # Store text in session state ratings
        if sample_id in st.session_state.ratings:
            st.session_state.ratings[sample_id]["text"] = text
        
        st.markdown(f'<div class="audio-container">', unsafe_allow_html=True)
        st.subheader(f"Sample {i+1} of 10")
        st.write(f"**Text:** {text}")
        
        # Update progress
        progress_text.text(f"Rating progress: {i+1}/10 samples")
        
        # Display four audio players in a row
        cols = st.columns(4)
        
        # Sort audio keys by position value to ensure they display in correct order
        sorted_audio_keys = sorted(audio_mapping.items(), key=lambda x: x[1])
        
        for position, (audio_key, position_value) in enumerate(sorted_audio_keys):
            with cols[position]:
                st.write(f"**Audio {position+1}**")
                
                # Construct audio path
                audio_path = f"./audios/audios_{sample_id}/{audio_key}.mp3"
                
                # Display actual audio player
                try:
                    st.audio(audio_path)
                except Exception as e:
                    st.error(f"Could not load audio: {e}")
                    st.markdown(f"*Audio would be at: {audio_path}*")
                
                # Get the model number from the audio_key
                model_id = None
                if audio_key == "audio1":
                    model_id = 3  # ElevenLabs
                elif audio_key == "audio2":
                    model_id = 2  # Google
                elif audio_key == "audio3":
                    model_id = 1  # AWS
                elif audio_key == "audio4":
                    model_id = 4  # Azure
                
                # Rating for this audio
                rating_key = f"{sample_id}_{audio_key}"
                
                # Check if this rating already exists in session state
                current_rating = 3  # Default rating
                if sample_id in st.session_state.ratings and \
                   "audio_ratings" in st.session_state.ratings[sample_id] and \
                   audio_key in st.session_state.ratings[sample_id]["audio_ratings"]:
                    current_rating = st.session_state.ratings[sample_id]["audio_ratings"][audio_key].get("rating", 3)
                
                # Add slider with on_change callback
                st.slider(
                    f"Rate Audio {position+1}",
                    min_value=1,
                    max_value=5,
                    value=current_rating,
                    key=rating_key,
                    on_change=update_rating,
                    args=(sample_id, audio_key, model_id, position+1)
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Ratings", type="primary", use_container_width=True):
            if save_ratings(st.session_state.ratings):
                st.session_state.submitted = True
                st.success("Your ratings have been submitted successfully!")
            else:
                st.error("There was an error saving your ratings.")
    
    # with col2:
    #     # Show current ratings in JSON format (for debugging)
    #     if st.button("Show Results Summary", use_container_width=True):
    #         # Create a summary of ratings by model
    #         model_ratings = {
    #             "ElevenLabs TTS": [],
    #             "Google TTS": [],
    #             "AWS Polly": [],
    #             "Azure TTS": []
    #         }
            
    #         for sample_id, data in st.session_state.ratings.items():
    #             for audio_key, rating_data in data.get("audio_ratings", {}).items():
    #                 model_name = rating_data.get("model_name")
    #                 if model_name in model_ratings:
    #                     model_ratings[model_name].append(rating_data.get("rating", 0))
            
    #         # Calculate averages
    #         summary = {}
    #         for model, ratings in model_ratings.items():
    #             if ratings:
    #                 summary[model] = {
    #                     "average": sum(ratings) / len(ratings) if ratings else 0,
    #                     "count": len(ratings),
    #                     "ratings": ratings
    #                 }
            
    #         st.subheader("Rating Summary by TTS Model")
    #         for model, data in summary.items():
    #             st.write(f"**{model}**: Average Rating: {data['average']:.2f} (from {data['count']} ratings)")
    
    # Show raw JSON data for debugging
    # if st.checkbox("Show raw ratings data (JSON)"):
    #     st.json(st.session_state.ratings)
    
    # If ratings were submitted, show a reset button
    # if st.session_state.submitted:
    #     if st.button("Rate more samples", use_container_width=True):
    #         # Flag to reload samples on next run
    #         st.session_state.reload_samples = True
    #         st.session_state.ratings = {}
    #         st.session_state.submitted = False
    #         st.experimental_rerun()

if __name__ == "__main__":
    main()

# import streamlit as st
# import json
# import os
# import random
# from datetime import datetime

# # Set page configuration
# st.set_page_config(page_title="TTS Model Rating System", layout="wide")

# # Style settings
# st.markdown("""
# <style>
#     .header {
#         font-size: 30px;
#         font-weight: bold;
#         margin-bottom: 20px;
#         text-align: center;
#     }
#     .audio-container {
#         background-color: #f0f2f6;
#         border-radius: 10px;
#         padding: 20px;
#         margin-bottom: 20px;
#     }
#     .rating-container {
#         display: flex;
#         flex-direction: column;
#         align-items: center;
#     }
#     .model-info {
#         font-size: 12px;
#         color: #666;
#         font-style: italic;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Function to load metadata and select random samples
# def load_metadata(file_path="new_metadata.json", num_samples=10):
#     if os.path.exists(file_path):
#         with open(file_path, "r") as f:
#             all_data = json.load(f)
#             # Select random samples if we have more than requested
#             if len(all_data) > num_samples:
#                 return random.sample(all_data, num_samples)
#             return all_data
#     else:
#         st.error(f"Metadata file not found at {file_path}")
#         return []

# # Model name mapping for reference (not shown to users during testing)
# MODEL_NAMES = {
#     1: "AWS Polly",
#     2: "Google TTS",
#     3: "ElevenLabs TTS",
#     4: "Azure TTS"
# }

# # Function to save results
# def save_ratings(ratings, file_path="ratings_results.json"):
#     # Create a timestamp for this submission
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
#     # Format the results
#     submission = {
#         "timestamp": timestamp,
#         "ratings": ratings
#     }
    
#     # Load existing results if any
#     all_results = []
#     if os.path.exists(file_path):
#         with open(file_path, "r") as f:
#             all_results = json.load(f)
    
#     # Add new submission
#     all_results.append(submission)
    
#     # Save back to file
#     with open(file_path, "w") as f:
#         json.dump(all_results, f, indent=4)
    
#     return True

# # Main app
# def main():
#     st.markdown('<div class="header">TTS Model Rating System</div>', unsafe_allow_html=True)
    
#     st.write("""
#     Listen to each audio sample and rate it from 1 to 5 stars.
#     The audios are randomized and anonymized - you won't know which TTS model produced which audio.
#     """)
    
#     # Load 10 random samples from metadata
#     samples = load_metadata(num_samples=10)
    
#     if not samples:
#         st.error("No samples were loaded. Please check your new_metadata.json file.")
#         return
    
#     # Initialize session state for ratings if not already done
#     if 'ratings' not in st.session_state:
#         # Create empty ratings dictionary with all sample IDs from the loaded samples
#         st.session_state.ratings = {}
#         for item in samples:
#             sample_id = item["id"]
#             st.session_state.ratings[sample_id] = {"text": item["text"], "audio_ratings": {}}
    
#     # Make sure all sample IDs exist in the ratings dictionary (in case new samples were loaded)
#     for item in samples:
#         sample_id = item["id"]
#         if sample_id not in st.session_state.ratings:
#             st.session_state.ratings[sample_id] = {"text": item["text"], "audio_ratings": {}}
    
#     if 'submitted' not in st.session_state:
#         st.session_state.submitted = False
    
#     # Show progress
#     progress_text = st.empty()
    
#     # Display each text sample with its audio options
#     for i, item in enumerate(samples):
#         sample_id = item["id"]
#         text = item["text"]
        
#         # Get the correct audio mapping key (audios_1, audios_2, etc.)
#         audio_key = f"audios_{sample_id}"
#         if audio_key not in item:
#             # Try alternate format if the key doesn't exist
#             audio_key = f"audios_{int(sample_id)}"
#             if audio_key not in item:
#                 st.warning(f"Could not find audio mapping for sample {sample_id}")
#                 continue
        
#         audio_mapping = item[audio_key]
        
#         st.markdown(f'<div class="audio-container">', unsafe_allow_html=True)
#         st.subheader(f"Sample {i+1} of 10")
#         st.write(f"**Text:** {text}")
        
#         # Update progress
#         progress_text.text(f"Rating progress: {i+1}/10 samples")
        
#         # Display four audio players in a row
#         cols = st.columns(4)
        
#         # Sort audio keys by position value to ensure they display in correct order
#         sorted_audio_keys = sorted(audio_mapping.items(), key=lambda x: x[1])
        
#         for position, (audio_key, position_value) in enumerate(sorted_audio_keys):
#             with cols[position]:
#                 st.write(f"**Audio {position+1}**")
                
#                 # Construct audio path
#                 audio_path = f"./audios/audios_{sample_id}/{audio_key}.mp3"
                
#                 # Display actual audio player
#                 try:
#                     st.audio(audio_path)
#                 except Exception as e:
#                     st.error(f"Could not load audio: {e}")
#                     st.markdown(f"*Audio would be at: {audio_path}*")
                
#                 # Rating for this audio
#                 rating_key = f"{sample_id}_{audio_key}"
#                 rating = st.slider(
#                     f"Rate Audio {position+1}",
#                     min_value=1,
#                     max_value=5,
#                     value=3,
#                     key=rating_key
#                 )
                
#                 # Get the model number from the audio_key
#                 # In your schema, audio1 is ElevenLabs (3), audio2 is Google (2), etc.
#                 model_id = None
#                 if audio_key == "audio1":
#                     model_id = 3  # ElevenLabs
#                 elif audio_key == "audio2":
#                     model_id = 2  # Google
#                 elif audio_key == "audio3":
#                     model_id = 1  # AWS
#                 elif audio_key == "audio4":
#                     model_id = 4  # Azure
                
#                 # Store the rating in session state
#                 st.session_state.ratings[sample_id]["audio_ratings"][audio_key] = {
#                     "display_position": position+1,
#                     "actual_model": model_id,
#                     "model_name": MODEL_NAMES.get(model_id, "Unknown"),
#                     "rating": rating
#                 }
        
#         st.markdown('</div>', unsafe_allow_html=True)
    
#     # Submit button
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Submit Ratings", type="primary", use_container_width=True):
#             if save_ratings(st.session_state.ratings):
#                 st.session_state.submitted = True
#                 st.success("Your ratings have been submitted successfully!")
#             else:
#                 st.error("There was an error saving your ratings.")
    
#     with col2:
#         # Show current ratings in JSON format (for debugging)
#         if st.button("Show Results Summary", use_container_width=True):
#             # Create a summary of ratings by model
#             model_ratings = {
#                 "ElevenLabs TTS": [],
#                 "Google TTS": [],
#                 "AWS Polly": [],
#                 "Azure TTS": []
#             }
            
#             for sample_id, data in st.session_state.ratings.items():
#                 for audio_key, rating_data in data.get("audio_ratings", {}).items():
#                     model_name = rating_data.get("model_name")
#                     if model_name in model_ratings:
#                         model_ratings[model_name].append(rating_data.get("rating", 0))
            
#             # Calculate averages
#             summary = {}
#             for model, ratings in model_ratings.items():
#                 if ratings:
#                     summary[model] = {
#                         "average": sum(ratings) / len(ratings) if ratings else 0,
#                         "count": len(ratings),
#                         "ratings": ratings
#                     }
            
#             st.subheader("Rating Summary by TTS Model")
#             for model, data in summary.items():
#                 st.write(f"**{model}**: Average Rating: {data['average']:.2f} (from {data['count']} ratings)")
    
#     # Show raw JSON data for debugging
#     if st.checkbox("Show raw ratings data (JSON)"):
#         st.json(st.session_state.ratings)
    
#     # If ratings were submitted, show a reset button
#     if st.session_state.submitted:
#         if st.button("Rate more samples", use_container_width=True):
#             # Load new samples for the next round
#             new_samples = load_metadata(num_samples=10)
#             # Reset the ratings for the new samples
#             st.session_state.ratings = {}
#             for item in new_samples:
#                 sample_id = item["id"]
#                 st.session_state.ratings[sample_id] = {"text": item["text"], "audio_ratings": {}}
#             st.session_state.submitted = False
#             st.experimental_rerun()

# if __name__ == "__main__":
#     main()


