import logging
import gallery_dl
import subprocess
logger = logging.getLogger(__name__)
class ImageDownloader:
    def __init__(self):
        pass
    
    def download_image(self, img_url: str, directory_savepath: str, save_as_filename: str) -> bool:
        # TODO: some sites requires prefix to invoke custom downloader
        # https://github.com/mikf/gallery-dl
        # Eg. gallery-dl "tumblr:https://sometumblrblog.example"
        result_int = 1
        # TODO: support different cookies for different platforms. Cookies need to be refreshed and updated periodically.
        # Alternatively, just don't logout.
        # TODO https://trello.com/c/pkVYTxns
        cookies_arg = "--cookies ./cookies_instagram.txt" 
        image_target = img_url
        save_file = "-D {0} -f {1}".format(directory_savepath, save_as_filename)

        args = "gallery-dl {0} {1} {2}"

        try:
            result_int = subprocess.call(args.format(save_file, cookies_arg, image_target), shell=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
        
        success_code = 0
        return result_int == success_code