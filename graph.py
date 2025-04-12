import csv, copy, math, requests
from typing import TypedDict, Optional, Any
from bs4 import BeautifulSoup
from typing import TypedDict, Optional
import plotly.graph_objects as go
from collections import defaultdict
import pandas as pd

class Movie(TypedDict):
    rating: Optional[float] # out of 5
    watched_date: str
    liked: bool
    rewatched: bool
    tags: list[str]
    
# Takes in a CSV file and returns the list of movies
def parse_letterboxd_history(diary_file: str, likes_file: str) -> dict[str, Movie]:
    movies: dict[str, Movie] = {}

    with open(diary_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            watched_date = row['Watched Date']
            name = row['Name']
            year = row['Year']
            rewatched = (row['Rewatch'] == 'Yes')
            if row['Rating'] == '':
                rating = None
            else:
                rating = float(row['Rating'])
            tags = row['Tags'].split(', ')

            movies[f'{name} ({year})'] = {
                'rating': rating,
                'watched_date': watched_date,
                'liked': False, # default to false
                'rewatched': rewatched,
                'tags': tags,
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
  
def get_watchlist(watchlist_file):
  watchlist = []
    # Mark liked movies
  with open(watchlist_file, newline='', encoding='utf-8') as file:
      reader = csv.DictReader(file)
      for row in reader:
          watchlist.append({
            'watched_date': row['Date'],
          })

  return watchlist
  
movies = parse_letterboxd_history('export/diary.csv', 'export/likes/films.csv').values()
watchlist = get_watchlist('export/watchlist.csv')

# Convert data into a DataFrame
df = pd.DataFrame(movies)
df['watched_date'] = pd.to_datetime(df['watched_date'])
df['rating'] = df['rating'].fillna(-1)

# Watchlist
df2 = pd.DataFrame(watchlist)
df2['watched_date'] = pd.to_datetime(df2['watched_date'])
grouped2 = df2.groupby('watched_date')
date_to_group_watchlist = {date: group for date, group in grouped2}

# Group by date
grouped = df.groupby('watched_date')
dates = []
total_count = []
liked_count = []
rewatched_count = []
watchlist_count = []
rating_counts = defaultdict(list)
tag_counts = defaultdict(list)

cumulative_total = 0
cumulative_liked = 0
cumulative_rewatched = 0
cumulative_watchlist = 0
cumulative_ratings = defaultdict(int)
cumulative_tags = defaultdict(int)

all_dates = pd.date_range(start=df['watched_date'].min(), end=df['watched_date'].max())
date_to_group = {date: group for date, group in grouped}

for date in all_dates:
  dates.append(date)
  if date in date_to_group:
    group = date_to_group[date]
    cumulative_total += len(group)
    cumulative_liked += group['liked'].sum()
    cumulative_rewatched += group['rewatched'].sum()

    all_tags = sum(group['tags'].tolist(), [])
    for tag in set(all_tags):
      count = all_tags.count(tag)
      cumulative_tags[tag] += count

    for rating in group['rating'].unique():
      count = len(group[group['rating'] == rating])
      cumulative_ratings[rating] += count
      
  if date in date_to_group_watchlist:
    cumulative_watchlist += len(date_to_group_watchlist[date])

  total_count.append(cumulative_total)
  liked_count.append(cumulative_liked)
  rewatched_count.append(cumulative_rewatched)
  watchlist_count.append(cumulative_watchlist)

  for rating in cumulative_ratings:
    rating_counts[rating].append(cumulative_ratings[rating])

  for tag in cumulative_tags:
    tag_counts[tag].append(cumulative_tags[tag])

# Fill gaps with zeros for ratings and tags before their first appearance
for rating in rating_counts:
  while len(rating_counts[rating]) < len(dates):
    rating_counts[rating].insert(0, 0)

for tag in tag_counts:
  while len(tag_counts[tag]) < len(dates):
    tag_counts[tag].insert(0, 0)

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=total_count, mode='lines', name='Total'))
fig.add_trace(go.Scatter(x=dates, y=liked_count, mode='lines', name='Liked'))
fig.add_trace(go.Scatter(x=dates, y=rewatched_count, mode='lines', name='Rewatched'))
fig.add_trace(go.Scatter(x=dates, y=watchlist_count, mode='lines', name='Watchlist'))

for rating, counts in rating_counts.items():
  if rating != -1:
    fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines', name=f'Rating {rating}'))

for tag, counts in tag_counts.items():
  fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines', name=f'Tag {tag}'))

fig.update_layout(title='Movies Watched Over Time (Cumulative)', xaxis_title='Date', yaxis_title='Number of Movies')

# Save as HTML
fig.write_html('movies_graph.html')
