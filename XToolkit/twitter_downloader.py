import yt_dlp
import os
from typing import Optional


class TwitterDownloader:
    def __init__(self):
        self.ydl_opts = {}

    def download_video(
        self,
        url: str,
        output_path: str,
        convert_to_gif: bool = False,
        progress_callback=None,
    ) -> bool:
        """下载 Twitter 视频"""
        try:
            ydl_opts = {"outtmpl": os.path.join(output_path, "%(title)s.%(ext)s")}

            if convert_to_gif:
                # 转换为 GIF 的选项
                ydl_opts["outtmpl"] = os.path.join(output_path, "%(title)s.gif")
                ydl_opts["postprocessors"] = [
                    {"key": "FFmpegVideoConvertor", "preferedformat": "gif"}
                ]

            if progress_callback:
                ydl_opts["progress_hooks"] = [progress_callback]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return True
        except Exception as e:
            raise Exception(f"下载失败: {e}")

    def get_video_info(self, url: str) -> dict:
        """获取视频基本信息（Twitter 通常不需要复杂检测）"""
        try:
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            raise Exception(f"获取视频信息失败: {e}")
