import yt_dlp
import os
from typing import Dict, List, Tuple, Optional


class YouTubeDownloader:
    def __init__(self):
        self.ydl_opts = {}

    def get_video_info(self, url: str) -> Dict:
        """获取视频信息"""
        try:
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            raise Exception(f"获取视频信息失败: {e}")

    def get_available_formats(self, info: Dict) -> List[Tuple[str, str]]:
        """获取可用格式"""
        formats = info.get("formats", [])
        available_formats = []

        for f in formats:
            if f.get("vcodec") != "none" and f.get("acodec") != "none":
                label = f"{f.get('format_id')} - {f.get('format_note', '')} - {f.get('ext')} - {f.get('height', '')}p"
                available_formats.append((label, f.get("format_id")))

        return available_formats

    def get_available_subtitles(self, info: Dict) -> List[Tuple[str, str]]:
        """获取可用字幕"""
        subtitles = info.get("subtitles", {})
        available_subtitles = [("无", "")]

        for lang in subtitles.keys():
            available_subtitles.append((lang, lang))

        return available_subtitles

    def download_video(
        self,
        url: str,
        output_path: str,
        format_id: Optional[str] = None,
        subtitle_lang: Optional[str] = None,
        progress_callback=None,
    ) -> bool:
        """下载视频"""
        try:
            ydl_opts = {"outtmpl": os.path.join(output_path, "%(title)s.%(ext)s")}

            if format_id:
                ydl_opts["format"] = format_id

            if subtitle_lang:
                ydl_opts["subtitleslangs"] = [subtitle_lang]
                ydl_opts["writesubtitles"] = True

            if progress_callback:
                ydl_opts["progress_hooks"] = [progress_callback]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return True
        except Exception as e:
            raise Exception(f"下载失败: {e}")
