from pytube import YouTube
import os

import yt_dlp

def download_video_yt_dlp(url, save_path=r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot", filename="video.mp4"):
    """
    Downloads a video using yt-dlp and saves it locally.
    """
    # options = {
    #     'outtmpl': f"{save_path}/{filename}",  # Save with the specified filename
    #     'format': 'bestvideo+bestaudio/best',  # Download best quality
    # }
    options = {
    'outtmpl': f"{save_path}/{filename}",
    'format': 'best',  # Download the best single format available
}
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            print(f"Downloading video from {url}...")
            ydl.download([url])
        print(f"Video downloaded successfully and saved as '{save_path}/{filename}'!")
    except Exception as e:
        print(f"An error occurred: {e}")



# Example usage
video_url = "https://www.youtube.com/watch?v=T9H_yu0Me8c"
download_video_yt_dlp(video_url)
