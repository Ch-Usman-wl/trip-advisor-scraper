In order to scrape from the website you would have to run the four scripts in order.

FIRSTLY:
Have a csv file that contains hotel name and the city+country (combined as one hopefully) it is in. Example:

"name", "city"
"AC Hotel Aitana", "Madrid, Spain"

In order to get the cookies/headers etc, I highly recommend watching this youtube video which will show you some parts and then come back and go through the rest.
https://www.youtube.com/watch?v=_wzFc_gPtV4

Lastly, I highly recommend using proxies as well.

SCRIPTS: changes and how they work

Run the Script called "Script_1.py"
This will create a csv file called "output.csv" that contains the query and the query for search. Be sure to change the name in the script to the csv file you have.

After it Run the script called "Script_2.py"
The script will run and get the hotelreview urls for each hotel and store them in a csv file called "urls1.csv"
Important Note: The script runs by doing a search on tripadvisor so make sure that the combination of hotel name + city does result in the hotel being the first result on the search page.

Changes:
Add the cookies, headers and json_data.
In the headers, change the referer as shown like this example: "'referer': f'https://www.tripadvisor.com/Search?q={url_query}....."
In the json_data, variables/events/routes, change the following to: "q": "{query}" and "referrer": "https://www.tripadvisor.com/Search?q={url_query}....
In the json_data, variables/requests, change the following to: 'query': f'{query}',


Next, Run the script called "Script_3.py"
This script will transform the urls retrieved from script 2 and get additional fields called hotel_id and geo_id/location_id and create a new csv file called extracted_urls2.csv


Finally run the script called "Script_4.py"
This script will start retrieving reviews from multiple hotels depending upon how many job workers are assigned in the script.

Changes:
add the cookies, headers and json_data.
In the headers, change the refere to the following: 'referer': f'https://www.tripadvisor.com{url}',
In json_data, variables/interactions/productinteractions/pageview/pageview_attributes, change the following to: 'location_id': hotel_id, and 'geo_id': location_id
In json_data, variables/interactions/productinteractions/items, change the following to: 'item_id': hotel_id,
In json_data, in variables, change the following to:
'variables': {
                    'hotelId': hotel_id,
                    'limit': 20,
                    'offset': offset,
                    'filters': [],
                    'language': 'en',
                },
(it will most likely be at the bottom in the json_data)


The final reviews will be stored in csv files that will be named as the location_id/geo_id. This is done so that a csv file doesn't become too cluttered and each location (example, Madrid, Spain) has its own reviews file.
The File will contain data as:
user_name,rating,title,description,language,date,total_reviews,hotel_id,geo_id



This is for educational purposes only.
