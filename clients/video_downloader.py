import logging
import yt_dlp
import os
import re
from typing import Optional, Dict, Any
from datetime import datetime
logger = logging.getLogger(__name__)
class VideoDownloader:
    def __init__(self):
        pass
    
    @staticmethod
    def progress_hook(d: Dict[str, Any]) -> bool:
        """
        Hook to display download progress
        
        Args:
            d (Dict[str, Any]): Progress information dictionary
        """
        if d['status'] == 'downloading':
            progress = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"Downloading: {progress} at {speed} ETA: {eta}", end='\r')
        elif d['status'] == 'finished':
            print("\nDownload completed, finalizing...")
    
    def download_video(self, video_url: str, custom_name: str) -> Optional[str]:
        filename = custom_name
        output_path = filename
        # TODO: Auth options: https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#authentication-options
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'best',
            'noplaylist': True,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            # TODO: support cookies https://trello.com/c/pkVYTxns
            #'cookiesfrombrowser': ('chrome',),  # Use Chrome cookies for authentication
            #'extractor_args': {'tiktok': {'webpage_download': True}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                return True
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Error downloading video: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
        
        return False