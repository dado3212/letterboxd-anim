import csv, copy
from typing import TypedDict, Optional

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

    print(len(movies))

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

    print(animation_slices[5])

def create_image(bucket_info: dict[float, list[Movie]]):
    return

# Example usage
parse_letterboxd_history('export/diary.csv')