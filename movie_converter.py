import os

from moviepy.editor import VideoFileClip

def get_output_format(input_path, format):
    filename, _ = os.path.splitext(input_path)
    return f"{filename}.{format}"

def convert_mov_to_mp4(input_path, converted_path):
    # Load the .mov file
    print("input", input_path)
    video_clip = VideoFileClip(input_path)
    # Write the video file to .mp4 format with audio, using a faster preset
    print("export", converted_path)
    video_clip.write_videofile(
        get_output_format(converted_path, 'mp4'),
        codec='libx264',
        audio_codec='aac',
        ffmpeg_params=['-preset', 'fast', '-crf', '23', '-threads', '4']
    )
    print(f"Processing {input_path}, duration: {video_clip.duration} seconds")
    video_clip.close()


# Example usage
input_path = ["copy_8F229B68-E86C-4B0D-AEF9-459921AA7120.MOV"]
output_path = ["copy_8F229B68-E86C-4B0D-AEF9-459921AA71201.mp4"]
for i in range(len(input_path)):
    convert_mov_to_mp4(input_path[i], output_path[i])
