import csv, copy, imageio
from typing import TypedDict, Optional, Any
from PIL import Image, ImageDraw, ImageFont

class Movie(TypedDict):
    name: str
    rating: Optional[float] # out of 5

# Takes in a CSV file and returns the list of movies
def parse_letterboxd_history(csv_file: str) -> dict[str, list[Movie]]:
    movies: dict[str, list[Movie]] = {}

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            watched_date = row['Watched Date']
            name = row['Name']
            if row['Rating'] == '':
                rating = None
            else:
                rating = float(row['Rating'])
            if watched_date not in movies:
                movies[watched_date] = []
                movies[watched_date].append({
                    'name': name,
                    'rating': rating,
                })
    return movies

# For a current distribution of movies, creates a single Image frame
def create_image(bucket_info: dict[float, list[Movie]], count: int):
    # Dimensions of the frames and GIF
    width: int = 256 # actually 250 on the website
    height: int = 80

    frame = Image.new('RGB', (width, height), '#14181c')

    # Create a drawing object
    draw = ImageDraw.Draw(frame)

    # Draw the ratings text
    text = 'RATINGS'
    font = ImageFont.truetype("fonts/Graphik-Regular-Web.woff", size=13)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_start_height = text_bbox[1]
    text_height = text_bbox[3]
    draw.text((1, 1), text, font=font, fill='#9ab')

    # Draw the number of reviews text
    text = str(count)
    font = ImageFont.truetype("fonts/Graphik-Regular-Web.woff", size=11)
    text_bbox = draw.textbbox((0, 0), text, font=font)

    draw.text((width - text_bbox[2] - 1, text_start_height + text_height - text_bbox[3]), text, font=font, fill='#678')

    # Draw the underline
    draw.line(
        (0, text_height + text_start_height + 5, width, text_height + text_start_height + 5),
        fill='#456',
        width=1
    )

    # Calculate the boxes that we're going to draw
    boxes: list[int] = []
    highest: int = 0
    for key in bucket_info.keys():
        count = len(bucket_info[key])
        boxes.append(count)
        if (count > highest):
            highest = count

    box_width = 17
    max_height = 44

    offset = 15

    for count in boxes:
        draw.rectangle((
            offset,
            height + 1,
            offset + box_width,
            height - (max_height * 1.0 * count / highest) - 1
        ), fill='#678')
        offset += box_width + 2

    # Append the frame to the list
    return frame

# Define the easing function
def ease(t: float) -> float:
    # Modify this function to customize the easing effect
    return t  # Linear easing, change to a different easing function as desired


# Takes in a list of movies and creates an animation
def create_and_save_animation(movies: dict[str, list[Movie]]):
    animation_slices: list[dict[float, list[Movie]]] = []

    current_buckets: dict[float, list[Movie]] = {
        0.5: [],
        1: [],
        1.5: [],
        2: [],
        2.5: [],
        3: [],
        3.5: [],
        4: [],
        4.5: [],
        5: [],
    }
    for key in sorted(movies.keys()):
        day_list = movies[key]
        for movie in day_list:
            rating = movie['rating']
            if rating is not None:
                current_buckets[rating].append(movie)
                animation_slices.append(copy.deepcopy(current_buckets))    

    # Create a list to store frames
    frames: list[Any] = []
    for i, slice in enumerate(animation_slices):
        frames.append(create_image(slice, i + 1))

    # Define the duration range (in seconds)
    min_duration = 0.1
    max_duration = 0.5
    target_duration_seconds = 5
    fps = round(len(movies) / target_duration_seconds)
    
    # Calculate the easing durations for each frame
    num_frames = len(frames)
    durations: list[float] = []
    for i in range(num_frames):
        t = i / (num_frames - 1)  # Normalized time between 0 and 1
        eased_t = ease(t)  # Apply easing function
        duration = min_duration + (max_duration - min_duration) * eased_t
        durations.append(duration)

    # Duplicate frames based on their durations
    duplicated_frames: list[Any] = []
    for frame, duration in zip(frames, durations):
        num_repetitions = int(duration * fps)
        duplicated_frames.extend([frame] * num_repetitions)

    # Save the frames as an animated mp4
    num_loops = 1
    imageio.mimsave('animation.mp4', frames * num_loops, fps=fps)

# Example usage
movies = parse_letterboxd_history('export/diary.csv')
create_and_save_animation(movies)