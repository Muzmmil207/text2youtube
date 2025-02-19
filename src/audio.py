from pydub import AudioSegment

from src.logger import logger

from .elevenlabs import ElevenLabsAPI


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000  # Convert milliseconds to seconds


def generate_voice_over(splitted_output: list, output_dir: str) -> float:
    """
    Generate voice-over audio from the given `splitted_output` and save it as a WAV file.

    :param splitted_output: A list of items representing the splitted output.
    :param output_dir: The output directory where the voice-over WAV file will be saved.
    :return: The duration of the generated voice-over audio in frames.
    """
    logger.info("Generate voiceover")

    output_text = " ".join(
        (item.text for item in splitted_output if item.type == "text")
    )

    file_path = f"{output_dir}/voiceover.wav"

    # Use ElevenLabsAPI to generate voice-over
    elevenlabs_api = ElevenLabsAPI()
    elevenlabs_api.generate_voice(
        text=output_text, character="Chris", filepath=file_path
    )

    logger.info(f"Voice over saved OK {file_path}")
    logger.info(
        f"ElevenLabs API remaining characters: {elevenlabs_api.get_remaining_characters()}"
    )

    # Calculate and return duration using get_audio_duration
    return get_audio_duration(file_path)
