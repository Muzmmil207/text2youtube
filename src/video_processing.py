from dataclasses import dataclass
from http.client import HTTPException
from pathlib import Path
from random import randint, sample
from typing import Union

from requests import get

from src.config import cfg
from src.logger import logger
from src.utils import Elem
from src.yt_download import download_yt_video


@dataclass
class Video:
    title: str
    duration: int
    url: str


def find_video(videos):
    target_width = 1280
    target_height = 720

    # Find the video with the target resolution
    for video in videos:
        if video['width'] == target_width and video['height'] == target_height:
            from dataclasses import dataclass
from http.client import HTTPException
from pathlib import Path
from random import randint, sample
from typing import Union

from requests import get

from src.config import cfg
from src.logger import logger
from src.utils import Elem
from src.yt_download import download_yt_video


@dataclass
class Video:
    title: str
    duration: int
    url: str


def find_video(videos):
    if not videos:
        return None

    target_width = 1280
    target_height = 720

    # Find the video with the target resolution
    for video in videos:
        if video.get('width') == target_width and video.get('height') == target_height:
            return video

    # If not found, find the best lower resolution video
    lower_quality_video = None
    for video in videos:
        width = video.get('width')
        height = video.get('height')
        if width and height and width < target_width and height < target_height:
            if lower_quality_video is None or (width > lower_quality_video.get('width', 0) and height > lower_quality_video.get('height', 0)):
                lower_quality_video = video
    
    if lower_quality_video:
        return lower_quality_video

    # As a last resort, return the first video in the list
    return videos[0]


def get_pexels_video_urls(search_terms: list[str], n_results: int) -> list[Video]:
    query_n_results = max(n_results, 10)

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": cfg.PEXELS_API_KEY}
    params = {
        "query": "-".join(search_terms),
        "orientation": "landscape",
        "per_page": query_n_results,
    }

    response = get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(f"Bad status code {response.status_code}")

    data = response.json()

    videos = []
    for item in data.get("videos", []):
        video_file = find_video(item.get("video_files", []))
        if video_file and video_file.get("link"):
            videos.append(
                Video(
                    "title",
                    int(item["duration"]),
                    video_file["link"],
                )
            )

    n_results = min(n_results, len(videos))
    if n_results == 0:
        return []

    return sample(
        videos,
        n_results,
    )


def save_videos(
    elements: list[Elem],
    total_duration: float,
    file_output_dir: Union[str, Path],
    yt_proba: int,
) -> None:
    """
    Save videos based on the provided `elements` and their durations.

    :param elements: A list of `Elem` objects representing the elements.
    :param total_duration: The total duration in seconds.
    :param file_output_dir: The directory where the videos will be saved.
    :param cookies: A `CookieJar` object containing the necessary cookies for authentication.
    :param yt_proba: Probability to use YouTube as a video source in percent

    :return: None
    """
    logger.info("Start video collection...")
    queries = [item.text for item in elements if item.type == "query"]
    durations = [
        item.percent * total_duration for item in elements if item.type == "text"
    ]
    for n_paragraph, (query, duration) in enumerate(zip(queries, durations)):
        if randint(0, 100) <= yt_proba:
            download_yt_video(duration, file_output_dir, n_paragraph, query)
        else:
            save_pexels(duration, file_output_dir, n_paragraph, query)


def save_pexels(
    duration: Union[int, float],
    file_output_dir: str,
    n_paragraph: int,
    query: str,
) -> None:
    """
    Save videos from pexels or fallback to saving from YouTube.

    :param duration: The desired total duration in seconds.
    :type duration: int
    :param file_output_dir: The directory where the videos will be saved.
    :type file_output_dir: str
    :param n_paragraph: The paragraph number.
    :type n_paragraph: int
    :param query: The search query for videos.
    :type query: str
    :return: None
    """
    videos: list[Video] = get_pexels_video_urls(
        query.split(),
        int(duration / 5),
    )
    if not videos:
        download_yt_video(duration, file_output_dir, n_paragraph, query)
        return
    # drop less relevant videos from the end, if sum duration is enough without them
    while (
        len(videos) > 1
        and sum((video.duration for video in videos)) - videos[-1].duration > duration
    ):
        videos.pop()
    # iterate through urls and save them in video folder
    for v_num, url in enumerate((video.url for video in videos)):
        v_path = f"{file_output_dir}/videos/{n_paragraph}_{v_num}.mp4"
        download_pexels_video(url, v_path)


def download_pexels_video(url: str, path: Union[str, Path]) -> None:
    """
    Downloads a video from the specified URL using the provided cookies and saves it to the given file path.

    :param url: The URL of the video to download.
    :type url: str
    :param path: The path where the downloaded video will be saved.
    :type path: Union[Path, str]
    :return: None
    """
    response = get(url)
    if response.status_code != 200:
        raise HTTPException(f"Bad status code {response.status_code}")

    with open(path, "wb") as file:
        file.write(response.content)
    
    # If not found, return the video with the next lower resolution
    lower_quality_video = videos[0]
    for video in videos:
        if video['width'] < target_width and video['height'] < target_height:
            if lower_quality_video is None or (
                video['width'] > lower_quality_video['width']
                and video['height'] > lower_quality_video['height']
            ):
                lower_quality_video = video

    return lower_quality_video


def get_pexels_video_urls(search_terms: list[str], n_results: int) -> list[Video]:
    query_n_results = max(n_results, 10)

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": cfg.PEXELS_API_KEY}
    params = {
        "query": "-".join(search_terms),
        "orientation": "landscape",
        "per_page": query_n_results,
    }

    response = get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(f"Bad status code {response.status_code}")

    data = response.json()

    n_results = min(n_results, len(data["videos"]))

    return sample(
        [
            Video(
                "title",
                int(item["duration"]),
                find_video(item["video_files"])["link"],
            )
            for item in data["videos"]
            if find_video(item["video_files"])["link"]
        ],
        n_results,
    )


def save_videos(
    elements: list[Elem],
    total_duration: float,
    file_output_dir: Union[str, Path],
    yt_proba: int,
) -> None:
    """
    Save videos based on the provided `elements` and their durations.

    :param elements: A list of `Elem` objects representing the elements.
    :param total_duration: The total duration in seconds.
    :param file_output_dir: The directory where the videos will be saved.
    :param cookies: A `CookieJar` object containing the necessary cookies for authentication.
    :param yt_proba: Probability to use YouTube as a video source in percent

    :return: None
    """
    logger.info("Start video collection...")
    queries = [item.text for item in elements if item.type == "query"]
    durations = [
        item.percent * total_duration for item in elements if item.type == "text"
    ]
    for n_paragraph, (query, duration) in enumerate(zip(queries, durations)):
        if randint(0, 100) <= yt_proba:
            download_yt_video(duration, file_output_dir, n_paragraph, query)
        else:
            save_pexels(duration, file_output_dir, n_paragraph, query)


def save_pexels(
    duration: Union[int, float],
    file_output_dir: str,
    n_paragraph: int,
    query: str,
) -> None:
    """
    Save videos from pexels or fallback to saving from YouTube.

    :param duration: The desired total duration in seconds.
    :type duration: int
    :param file_output_dir: The directory where the videos will be saved.
    :type file_output_dir: str
    :param n_paragraph: The paragraph number.
    :type n_paragraph: int
    :param query: The search query for videos.
    :type query: str
    :return: None
    """
    videos: list[Video] = get_pexels_video_urls(
        query.split(),
        int(duration / 5),
    )
    if not videos:
        download_yt_video(duration, file_output_dir, n_paragraph, query)
        return
    # drop less relevant videos from the end, if sum duration is enough without them
    while (
        len(videos) > 1
        and sum((video.duration for video in videos)) - videos[-1].duration > duration
    ):
        videos.pop()
    # iterate through urls and save them in video folder
    for v_num, url in enumerate((video.url for video in videos)):
        v_path = f"{file_output_dir}/videos/{n_paragraph}_{v_num}.mp4"
        download_pexels_video(url, v_path)


def download_pexels_video(url: str, path: Union[str, Path]) -> None:
    """
    Downloads a video from the specified URL using the provided cookies and saves it to the given file path.

    :param url: The URL of the video to download.
    :type url: str
    :param path: The path where the downloaded video will be saved.
    :type path: Union[Path, str]
    :return: None
    """
    response = get(url)
    if response.status_code != 200:
        raise HTTPException(f"Bad status code {response.status_code}")

    with open(path, "wb") as file:
        file.write(response.content)
