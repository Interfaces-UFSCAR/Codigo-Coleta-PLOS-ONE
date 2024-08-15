#bibliotecas
import pandas as pd
import os
from datetime import datetime, timedelta

#variaveis globais
_tweets_dtype = {
    'id': str,
    'text': str,
    'created_at': str,
    'source': str,
    'lang': str,
    'conversation_id': str,
    'like_count': str,
    'retweet_count': str,
    'quote_count': str,
    'reply_count': str,
    'type': str,
    'referenced_tweet_id': str,
    'mentions': str,
    'hashtags': str,
    'hastags': str,
    'urls': str,
    'author_id': str,
    'media_keys': str
}

_users_dtype = {
    'account_id': str,
    'account_username': str,
    'account_created_at': str,
    'account_verified': bool,
    'account_protected': bool,
    'account_location': str,
    'account_have_profile_image': str,
    'account_followers_count': str,
    'account_following_count': str,
    'account_tweets_count': str,
}

_media_dtype = {
    'media_key': str,
    'media_type': str,
    'media_url': str,
    'media_view_count': str
}

_interaction_dtype = {
    'account_id': str,
    'tweet_id': str,
    'interaction_authors': str,
    'interaction_ids': str
}

#funcoes

#Cria diretorios pais caso não existam
def _make_dir(dir: str):
    father_dir = dir[:dir.rfind('/')]

    if not os.path.exists(father_dir):
        _make_dir(father_dir)
    os.mkdir(dir)

def _count_vector(x) -> int:
    if type(x) == str:
        return x.count(', ') + 1
    else:
        return 0

#Lida com um erro de alguns csvs antigos do início da codificação da coleta
def _read_csv(dir, dtype):
    try:
        df = pd.read_csv(dir, sep=';', escapechar= '\\', dtype= dtype, on_bad_lines= "warn", low_memory= False)
    except pd.errors.ParserError:
        df = pd.read_csv(dir, sep=';', escapechar= '\\', lineterminator= '\n', dtype= dtype, on_bad_lines= "warn", low_memory= False)
    except ValueError:
        df = pd.read_csv(dir, sep=';', escapechar= '\\', dtype= str, on_bad_lines= "warn", low_memory= False)
        col1 = df.columns[0]
        df = df[df[col1] != col1]
        df.reset_index(drop= True, inplace= True)

    return df

#Refatora o csv, armazenando com um nome melhor e num formato mais leve 
def _csv_refactor(dir, q, date: datetime, suffix = ''):
    global _tweets_dtype, _user_dtype, _media_dtype, _interaction_dtype

    typ = '_'
    name = ''
    df = None
    newdir = '../corpus/'
    namefile = (('-' + suffix) if(suffix != '')else '') + '-' + q + date.strftime('-%Y_%m_%d') + '.parquet'
    bad_lines = 0
    
    #cria diretório caso não exista
    if not os.path.exists(newdir):
        _make_dir(newdir[:-1])

    if('tweets' in dir[dir.rfind('/')+1:]):
        df = _read_csv(dir, dtype= _tweets_dtype)
        name = newdir + 'tweets' + namefile
        typ = 'tweets'

        #remove problemas de separador de linha
        df['id'].apply(lambda x: x.strip('\n ') if type(x) == str else x) 
        df['media_keys'].apply(lambda x: x.strip('\r ') if type(x) == str else x)

        #remove retweets dos primeiros dias em que era coletado junto
        if ('retweets' not in q):
            df = df[df['type'] != 'retweeted']
            df.reset_index(drop= True, inplace= True)

        #reove linhas corrompidas
        bad_lines = df.shape[0]

        df = df[df['type'].isin(['replied_to', 'quoted, replied_to', 'tweeted', 'quoted', 'retweeted'])]
        
        bad_lines -= df.shape[0]

        print(f'csv {typ + suffix}-{date}: {bad_lines} corrupted lines')

        #count vectors
        df['hashtags_count'] = df['hashtags'].apply(_count_vector)
        df['urls_count'] = df['urls'].apply(_count_vector)
        df['mentions_count'] = df['mentions'].apply(_count_vector)
        df['media_keys_count'] = df['media_keys'].apply(_count_vector)

        

    elif('users' in dir[dir.rfind('/')+1:]):
        df = _read_csv(dir, dtype= _users_dtype)
        name = newdir + 'users' + namefile
        typ = 'users'

        #remove problems in begin and end of line 
        df['account_id'].apply(lambda x: x.strip('\n ') if type(x) == str else x)
        df['account_tweets_count'].apply(lambda x: x.strip('\r ') if type(x) == str else x)

    elif('media' in dir[dir.rfind('/')+1:]):
        df = _read_csv(dir, dtype= _media_dtype)
        name = newdir + 'media' + namefile
        typ = 'media'

        #remove problemas de separador de linha
        df['media_key'].apply(lambda x: x.strip('\n ') if type(x) == str else x)
        df['media_view_count'].apply(lambda x: x.strip('\r ') if type(x) == str else x)

        #remove os links de thum dos videos e gifs
        df_img = df[df['media_type'] == 'photo']
        df_not_img = df[df['media_type'] != 'photo']
        df_not_img.loc[:,'media_url'] = df_not_img['media_url'].size*[None]

        df = pd.concat([df_img, df_not_img])

    elif('quotes' in dir[dir.rfind('/')+1:]):
        df = _read_csv(dir, dtype= _interaction_dtype)
        name = newdir + 'quotes' + namefile
        typ = 'quotecsv'

        #remove problemas de separador de linha
        df['account_id'].apply(lambda x: x.strip('\n ') if type(x) == str else x)
        df['interaction_ids'].apply(lambda x: x.strip('\r ') if type(x) == str else x)

    elif('replies' in dir[dir.rfind('/')+1:]):
        df = _read_csv(dir, dtype= _interaction_dtype)
        name = newdir + 'replies' + namefile
        typ = 'repliecsv'

        #remove problemas de separador de linha
        df['account_id'].apply(lambda x: x.strip('\n ') if type(x) == str else x)
        df['interaction_ids'].apply(lambda x: x.strip('\r ') if type(x) == str else x)

    # remove headers
    if df[df.columns[1]].isin([df.columns[1]]).any():
        df = df[df[df.columns[1]] != df.columns[1]]

    df.to_parquet(name)
    
    return typ
#

def _refactor_folder(dir, q, date: datetime, suffix = ''):
    csvs_type_count = {}
    files = []
    
    if(os.path.exists(dir)):
        files = os.listdir(dir)

    try:
        for file in files:
            aux = dir + file

            # refatora as pastas quotes e replies
            if (file == 'quotes' or file == 'replies'):
                _refactor_folder(aux + '/', q, date, suffix= file)

            elif ('likes' not in file and 'retweets' not in file):
                typ = _csv_refactor(aux, q, date, suffix)

                #garante que não há conflito de arquivos
                
                try:
                    csvs_type_count[typ]
                except KeyError:
                    csvs_type_count[typ] = True
                else:
                    print('Arquivos conflitantes')
                    input('Quando resolver digite qualquer coisa')
                    raise AssertionError
                    #
                #
                print(file, ' OK')

    except AssertionError:
        _refactor_folder(dir, q, date)


def refactor(root: str):
    data_dir = root + 'Eleicoes_2022_Pesquisa/coleta/hashtags/'
    queries_dirs = os.listdir(data_dir)


    #varrendo diretorios
    for q in queries_dirs:
        date = datetime(2023, 2, 1)
        end = datetime(2023, 2, 24)

        while date < end:
            print(f'\n{q}: {date.strftime("%d/%m/%Y")}')
            _refactor_folder(f'{data_dir}/{q}/{date.strftime("%Y/%m/%d")}/', q, date)

            date += timedelta(days=1)
            
        #
    #
#             

refactor('../coleta-dados-twitter-VINI/')
