import csv, copy, math, requests
from typing import TypedDict, Optional, Any
from bs4 import BeautifulSoup

class Movie(TypedDict):
    name: str
    rating: Optional[float] # out of 5
    watched_date: str
    liked: bool
    rewatched: bool
    url: str
    image: Optional[str]

# Takes in a CSV file and returns the list of movies
def parse_letterboxd_history(diary_file: str, likes_file: str) -> dict[str, Movie]:
    movies: dict[str, Movie] = {}

    with open(diary_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            watched_date = row['Watched Date']
            name = row['Name']
            year = row['Year']
            url = row['Letterboxd URI']
            rewatched = (row['Rewatch'] == 'Yes')
            if row['Rating'] == '':
                rating = None
            else:
                rating = float(row['Rating'])

            movies[f'{name} ({year})'] = {
                'name': name,
                'year': year,
                'rating': rating,
                'watched_date': watched_date,
                'liked': False, # default to false
                'rewatched': rewatched,
                'url': url,
            }

    # Mark liked movies
    with open(likes_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']
            year = row['Year']

            index_name = f'{name} ({year})'

            if index_name in movies:
                movies[index_name]['liked'] = True

    return movies

def with_photos(all_movies: dict[str, Movie], month_url: str) -> dict[str, Movie]:
    response = requests.get(month_url)

    movies: dict[str, Movie] = {}

    if response.status_code == 200:
        html_content = response.text
    else:
        raise Exception("Failed to retrieve the web page")

    soup = BeautifulSoup(html_content, 'html.parser')

    all_reviews = soup.find_all('tr', class_='diary-entry-row')

    for review in all_reviews:
        film_poster = review.find('div', class_='linked-film-poster')
        name = next(review.find('h3', class_='headline-3').children).contents[0]
        year = next(review.find('td', class_='td-released').children).contents[0]

        # 300x450
        poster_uri = 'https://letterboxd.com/ajax/poster/film/' + film_poster.get('data-film-slug') + '/std/500x750/'
        poster_response = requests.get(poster_uri)

        poster_soup = BeautifulSoup(poster_response.text, 'html.parser')
        img_element = poster_soup.find('img', class_='image')

        src_url = img_element.get('src')

        index_name = f'{name} ({year})'
        if index_name in all_movies:
            movies[index_name] = all_movies[index_name]
            movies[index_name]['image'] = src_url

    return movies

def create_website(movies: dict[str, Movie]):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Letterboxd Diary Month</title>
        <style>
            body {
                background-color: rgb(20, 24, 28);
                color: rgb(85, 102, 119);

                display: grid;
                justify-content: center;
                gap: 10px;
                margin: 20px 0;
                
                font-size: 1.2em;
            }

            .movie {
                position: relative;
            }

            .title {
                display: none;
            }

            img.poster {
                width: 100%;
                border-radius: 4px;
                border: 1px solid #ddeeff96;
            }

            .liked {
                display: inline-block;
                transform: scaleX(1.3);
                position: relative;
                bottom: 4px;
                right: -3px;
            }

            .rating {
                position: relative;
                top: -5px;
            }

            .rewatched {
                position: absolute;
                top: 0px;
                right: 0px;
                font-size: 30px;
                padding: 2px 2px 4px 4px;
                background: linear-gradient(45deg, transparent 0%, transparent 50%, rgb(0 0 0 / 77%) 53%, #1A5AB6 53%, #1A5AB6 100%);
                width: 40px;
                height: 42px;
                color: white;
                border-top-right-radius: 4px;
                text-align: right;
                vertical-align: top;
                line-height: 16px;
        }
        </style>
        <script>
            // Function to calculate the grid layout
            function calculateGridLayout() {
                const screenWidth = window.innerWidth - 30;
                const screenHeight = window.innerHeight - 70;

                const elementWidth = 30;
                const elementHeight = 45;
                const padding = 10;
                const verticalAdd = 27;
                const elementAspectRatio = elementWidth / elementHeight;

                let isHorizontalLayout = true;

                // Determine if the screen is taller than the element
                if (screenWidth / screenHeight < elementAspectRatio) {
                    isHorizontalLayout = false;
                }

                let minRow, maxRow, optimalColumns, optimalWidth, width, height;
    """
    html_content += "let numMovies = {num_movies}".format(num_movies=len(movies))
    html_content += """
                if (isHorizontalLayout) {
                    minRow = 1
                    maxRow = Math.floor(Math.sqrt(numMovies));
                } else {
                    minRow = Math.floor(Math.sqrt(numMovies)) - 1;
                    maxRow = numMovies;
                }

                let coverage = 0;
                for (var rows = minRow; rows <= maxRow; rows++) {
                    let columns = Math.ceil(numMovies / rows);

                    let maxSizedWidth = (screenWidth - (columns - 1) * padding) / columns;
                    let maxSizedHeight = (screenHeight - (rows - 1) * padding - rows * verticalAdd) / rows;

                    if (maxSizedWidth * elementHeight / elementWidth < maxSizedHeight) {
                        width = maxSizedWidth;
                        height = maxSizedWidth * elementHeight / elementWidth;
                    } else {
                        width = maxSizedHeight * elementWidth / elementHeight;
                        height = maxSizedHeight;
                    }

                    const currentCoverage = (width * columns) * (height * rows) / (screenWidth * screenHeight);

                    if (currentCoverage > coverage) {
                        coverage = currentCoverage;
                        optimalColumns = columns;
                        optimalWidth = width;
                    }
                }

                document.body.style.gridTemplateColumns = 'repeat(' + optimalColumns + ', auto)';
                document.querySelectorAll('.movie').forEach(element => {
                    element.style.width = optimalWidth + 'px';
                });
            }

            // Call the function on page load
            window.addEventListener('load', calculateGridLayout);
            // and reload
            window.addEventListener('resize', calculateGridLayout);
        </script>
    </head>
    <body>
    """
    # html_content += "<ul>\n"
    for movie_name in movies:
        movie = movies[movie_name]
        rating = ''
        if movie['rating'] is not None:
            for i in range(math.floor(movie['rating'])):
                rating += '★'
            if (movie['rating'] % 1 == 0.5):
                rating += '½'

        html_content += '''
            <div class='movie'>
            <span class='title'>{name}</span>
            <img class='poster' src='{image}'>
            <span class='rating'>{rating}</span>
        '''.format(name=movie['name'], image=movie['image'], rating=rating)
        if (movie['liked']):
            html_content += "<span class='liked'>♥</span>"
        if (movie['rewatched']):
            html_content += "<span class='rewatched'>⟳</span>"

        html_content += "</div>\n"

    html_content += "</body>\n</html>"

    # Save the HTML content to a file
    with open("index.html", "w") as html_file:
        html_file.write(html_content)

movies = parse_letterboxd_history('export/diary.csv', 'export/likes/films.csv')
# Set this to whatever month you want
movies = with_photos(movies, 'https://letterboxd.com/dado3212/films/diary/for/2025/03/')
create_website(dict(reversed(movies.items())))
