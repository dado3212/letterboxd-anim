import csv, copy, imageio
from typing import TypedDict, Optional, Any
from PIL import Image, ImageDraw, ImageFont

class Movie(TypedDict):
    name: str
    rating: Optional[float] # out of 5

def parse_letterboxd_history(csv_file: str):
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
       

    # Save the frames as an animated mp4
    target_duration_seconds = 5

    num_loops = 3
    imageio.mimsave('animation.mp4', frames * num_loops, fps=round(len(movies) / target_duration_seconds))

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

# Example usage
parse_letterboxd_history('export/diary.csv')