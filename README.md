# scraping-code-PLOS-ONE
Repository with the code related to the article publication regarding the construction of the ITED-Br dataset and its characteristics.

# About the Code

The ITED-Br dataset was assembled using two files: a Jupyter Notebook named `coleta.ipynb` for data collection and a Python script named `corpus_refactor.py` that refines the dataset, standardizing and adding elements to the files.

## `coleta.ipynb`

The code in the Jupyter Notebook ensures uninterrupted tweet collection by incorporating error handling for network issues and providing backup and state-saving mechanisms to mitigate the impact of adverse events like power outages. The collection stages and strategies used to manage the limitations of academic API access are detailed in our article. One key strategy was the rotation of tokens (token farming), cyclically swapping out tokens that temporarily reached their collection limit for those with available limits.

The code utilizes Python, along with the Tweepy and Pandas libraries, for making requests and structuring/storing the data, respectively. Initially, the data was saved in CSV (Comma Separated Values) format. This format allows new data to be appended continuously, ensuring backup functionality. However, it is inefficient in terms of reading and storage. Additionally, the code was adapted during the collection process, leading to a lack of standardization in the CSV files.

Thus, the `corpus_refactor.py` script was created to restructure the entire dataset without losing information.

## `corpus_refactor.py`

The CSV files generated by `coleta.ipynb` presented several challenges:

* File names were not accessible, requiring access to a JSON to search for the date and obtain the file;
* Changes during the collection process caused a lack of standardization in the CSV files, especially in the first month, complicating data reading;
* The CSV file format is inefficient in terms of disk reading time and storage space;
* Some derived data could be extracted from the collected data to aid in dataset manipulation.

The script opens all CSV files from the collection and saves them in Parquet format, reducing the physical volume of data, which is desirable when handling large datasets. It also renames the files with a specific pattern, which is presented later. Finally, it addresses the lack of standardization during reading and creates columns with information about the length of some vectors in the dataset.

# Dataset Organization
The dataset is organized based on the **query** used, the **date** of the tweets, and the **type** of data file. Thus, the directory for any file can be constructed as `.../corpus/query/year/month/day/`, and the file name can be constructed as `type-year_month_day-query.parquet`.

## Data Files

There are five types of data files: tweets, users, media, replies, and quotes.

### Tweets

The tweet files store collected tweets and their information:

| Column             | Definition                                           | Type                                                                            |
|--------------------|------------------------------------------------------|--------------------------------------------------------------------------------:|
| id                 | Tweet identification code                            | string                                                                         |
| text               | Tweet text                                           | string                                                                         |
| created_at         | Tweet creation date                                  | date                                                                           |
| source             | Tweet source (device or connected website)           | string                                                                         |
| lang               | Tweet language                                       | string                                                                         |
| conversation_id    | Identification code for all replies involving the tweet | string                                                                         |
| like_count         | Number of likes                                      | integer                                                                        |
| retweet_count      | Number of retweets                                   | integer                                                                        |
| quote_count        | Number of quotes                                     | integer                                                                        |
| reply_count        | Number of replies                                    | integer                                                                        |
| type               | Type (tweeted, retweeted, quoted, or replied_to)     | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| referenced_tweet_id| Identification code of the referenced tweet if type is not tweet | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| mentions           | Users mentioned in the tweet text                    | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| urls               | URLs in the tweet text                               | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| hashtags           | Hashtags in the tweet text                           | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| author_id          | Author identification code, also used to find the author in the authors file | string                                                                         |
| media_keys         | Media identification code, also used to find the media in the media files | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings* |
| mentions_count     | Length of the mentions vector                        | integer                                                                        |
| urls_count         | Length of the URLs vector                            | integer                                                                        |
| hashtags_count     | Length of the hashtags vector                        | integer                                                                        |
| media_keys_count   | Length of the media keys vector                      | integer                                                                        |

### Users

The user files store information about the users who posted the collected tweets.

| Column                 | Definition                       | Type      |
|------------------------|----------------------------------|----------:|
| account_id             | Author identification code       | string    |
| account_username       | Author's username                | string    |
| account_created_at     | Account creation date            | date      |
| account_verified       | Whether the account is verified  | boolean   |
| account_protected      | Whether the account is protected | boolean   |
| account_location       | Location field text              | string    |
| account_have_profile_image | Whether the account has a profile image | boolean   |
| account_followers_count| Number of followers              | integer   |
| account_following_count| Number of followed accounts      | integer   |
| account_tweets_count   | Number of tweets by the account  | integer   |

A single author may appear in multiple user files, as no duplicate user cleanup was performed, allowing analysis of the user's attribute evolution on the network over time.

### Media

The media files store information about the media in the collected tweets.

| Column    | Definition                        | Type    |
|-----------|-----------------------------------|--------:|
| media_key | Media identification code         | string  |
| media_type| Type of media (photo, video, or GIF)| string  |
| media_url | Link to the media                 | string  |

Only the links were collected.

### Interactions

In profile queries, replies and quotes of the collected tweets were gathered. Both types of files have the same structure.

| Column            | Definition                                       | Type    |
|-------------------|--------------------------------------------------|--------:|
| account_id        | Author identification code                       | string  |
| tweet_id          | Tweet identification code                        | string  |
| interaction_authors| Vector with IDs of authors who interacted       | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings |
| interaction_ids   | Vector with IDs of interaction tweets            | [vector](#vectors-are-not-supported-in-these-files-thus-the-vectors-are-comma-separated-values-that-can-be-easily-converted-to-python-lists-using-the-following-function) of strings |

Additionally, on the days of these profile queries, subfolders named after the interaction (quotes, replies, etc.) contain tweet, user, and media files with information from the corresponding interaction file.

---

### **In the generated files, vectors are comma-separated values (contained within a string), which can be easily converted to Python lists using the following function:**

```python
def convert_to_list(value):
    return value.split(',')
```

## Example of How to Open a File in Python:
```python
import pandas as pd

query = 'query_bolsonaro'
year = '2022'
month = '10'
day = '16'
type = 'tweets'

directory = f'./corpus/{query}/{year}/{month}/{day}/{type}-{year}_{month}_{day}-{query}.parquet'

data = pd.read_parquet(directory)
```
or

```python
import pandas as pd
from datetime import datetime

query = 'query_bolsonaro'
date = datetime(2022, 10, 16)
type = 'tweets'

directory = f'./corpus/{query}/{date.strftime("%Y/%m/%d")}/{type}-{date.strftime("%Y_%m_%d")}-{query}.parquet'

data = pd.read_parquet(directory)
```

## Number of Collected Tweets
| Query                  | Number of Tweets  |
|------------------------|------------------:|
| retweets_query_bolsonaro | 84,093,716 |
| retweets_query_lula      | 67,665,980 |
| query_bolsonaro          | 37,158,316 |
| query_lula               | 35,179,413 |
| retweets_pos_eleicao     | 10,055,682 |
| perfil_lula              | 6,955,987  |
| retweets_query_ciro      | 6,405,281  |
| pos_eleicao              | 6,277,433  |
| query_ciro               | 5,452,873  |
| atos_golpistas           | 4,466,959  |
| retweets_numero_bolsonaro| 3,178,076  |
| numero_lula              | 2,823,953  |
| numero_bolsonaro         | 2,684,908  |
| retweets_numero_lula     | 2,663,657  |
| perfil_bolsonaro         | 2,238,217  |
| retweets_query_simone    | 2,192,005  |
| query_simone             | 1,070,541  |
| perfil_simone            | 835,412    |
| perfil_ciro              | 737,163    |

# DOI
https://zenodo.org/doi/10.5281/zenodo.13124582

# Data Usage Agreement
This software and its source code are licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License (CC BY-NC-SA 4.0). By using either, you agree to abide by the stipulations in the license and cite the following manuscript:
Iasulaitis, S.; Valejo, A.D; Greco, B.C; Perillo, V.G; Messias, G.H; Vicari, I. The Interfaces Twitter Elections Dataset: Construction process and characteristics of Big Social Data during the 2022 presidential elections in Brazil. PLOS ONE (2024). (PUBLICATION DOI PLACEHOLDER)
