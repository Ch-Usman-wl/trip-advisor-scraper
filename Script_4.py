import requests
import pandas as pd
import os
from datetime import datetime
import time
import random
from joblib import Parallel, delayed
import threading

'''
Hotel 677803, (location 528813), offset: 1020: Waiting 5 seconds to not get flagged/blocked.
Reviews saved to 'Reviews appended'. 192033
Hotel 192033, (location 186338), offset: 1060: Waiting 9 seconds to not get flagged/blocked.
Reviews saved to 'Reviews appended'. 187735
Hotel 187735, (location 186338), offset: 2120: Waiting 9 seconds to not get flagged/blocked.
Reviews saved to 'Reviews appended'. 677803
'''
# Function to fetch reviews for a given hotel
def get_reviews(url, location_id, hotel_id, file_lock):
    total_reviews = 0
    reviews_per_page = 20
    total_pages = 1
    offset = 0
    get_pages = 0
    reviews_data = []

    cookies = {}

    headers = {}

    while True:
        json_data = [
            ]

        retries = 5
        random_wait = random.randint(5,9)
        print(f"Hotel {hotel_id}, (location {location_id}), offset: {offset}: Waiting {random_wait} seconds to not get flagged/blocked.")
        time.sleep(random_wait)
        response = None

        for attempt in range(retries):
            try:
                response = requests.post('https://www.tripadvisor.com/data/graphql/ids', cookies=cookies, headers=headers, json=json_data, timeout=10)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 4:
                    err = [{
                        'url': url,
                        'location_id': location_id,
                        'hotel_id': hotel_id,
                        'offset': offset,
                        'reviews_per_page': reviews_per_page,
                    }]
                    total_reviews = 0
                    reviews_per_page = 20
                    total_pages = 1
                    offset = 0
                    get_pages = 0
                    reviews_data.clear()
                    df_err = pd.DataFrame(err)
                    filename = 'errors_reviews.csv'

                    if not os.path.isfile(filename):
                        df_err.to_csv(filename, index=False)
                        print('File created: ', filename)
                    else:
                        df_err.to_csv(filename, mode='a', header=False, index=False)
                    print("Failed to get data, after 5 retries so moving on to next hotel.")
                    break
                else:
                    print('Waiting 10 seconds to retry...')
                    time.sleep(10)
        
        if response:
            resp = response.json()
            for item in resp:
                data = item.get('data')
                if data and "ReviewsProxy_getReviewListPageForLocation" in data:
                    review_cluster = data['ReviewsProxy_getReviewListPageForLocation']
                    if get_pages == 0:
                        total_reviews = review_cluster[0].get('totalCount', 0)
                        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page
                        get_pages = 1
                    reviews_list = review_cluster[0].get('reviews', [])
                    for review in reviews_list:
                        rating = review.get('rating', None)
                        title = review.get('title', None)
                        description = review.get('text', None)
                        language = review.get('language', None)
                        user_profile = review.get('userProfile', {})
                        user_name = user_profile.get('displayName', None) if user_profile else None
                        published_date = review.get('publishedDate', None)
                        date = datetime.strptime(published_date, "%Y-%m-%d") if published_date else None
                        value_rating = None
                        clean_rating = None
                        location_rating = None
                        service_rating = None
                        additional_ratings = review.get('additionalRatings', [])
                        if additional_ratings:
                            for add_ratings in additional_ratings:
                                label = add_ratings['ratingLabelLocalizedString']
                                if label == 'Value':
                                    value_rating = add_ratings['rating']
                                if label == 'Cleanliness':
                                    clean_rating = add_ratings['rating']
                                if label == 'Location':
                                    location_rating = add_ratings['rating']
                                if label == 'Service':
                                    service_rating = add_ratings['rating']

                        reviews_data.append({
                            'user_name': user_name,
                            'rating': rating,
                            'title': title,
                            'language': language,
                            'date': date,
                            'total_reviews': total_reviews,
                            'hotel_id': hotel_id,
                            'geo_id': location_id,
                            'value_rating': value_rating,
                            'clean_rating': clean_rating,
                            'location_rating': location_rating,
                            'service_rating': service_rating,
                            'description': description
                        })
                        print(f'Username: {user_name}, Rating: {rating}, Cleanliness Rating: {clean_rating}, Location Rating: {location_rating}, Service Rating: {service_rating}, Value Rating: {value_rating}')

        if reviews_data:
            filename = f'{location_id}.csv'
            df = pd.DataFrame(reviews_data)

            # Acquire lock before writing to the file
            with file_lock:
                if not os.path.isfile(filename):
                    df.to_csv(filename, index=False)
                    print(f'File created: {filename}')
                else:
                    df.to_csv(filename, mode='a', header=False, index=False)
            print(f"Reviews saved to 'Reviews appended'. {hotel_id}")
            reviews_data.clear()

        offset += reviews_per_page
        if offset >= total_reviews:
            print("Breaking this loop.")
            total_reviews = 0
            reviews_per_page = 20
            total_pages = 1
            offset = 0
            get_pages = 0
            reviews_data.clear()
            break
        if True:
            break

# Function to run each row in parallel
def run_reviews_parallel(row):
    file_lock = threading.Lock()

    url = row['hotel_review_urls']
    location_id = row['location_id']
    hotel_id = row['hotel_id']
    get_reviews(url, location_id, hotel_id, file_lock)

# Main function to read CSV and run multi-threading
def main():
    df = pd.read_csv('extracted_urls2.csv')  # Load the CSV file with hotel URLs

    Parallel(n_jobs=3)(delayed(run_reviews_parallel)(row) for index, row in df.iterrows())

if __name__ == '__main__':
    main()