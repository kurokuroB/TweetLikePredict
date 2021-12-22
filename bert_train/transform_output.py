import pandas as pd
import os
from glob import glob
import json
from tqdm import tqdm

tweet_jsons=sorted(glob(f'{os.path.dirname(__file__)}/output/*'))

tweet_public_metrics_keys = ['like_count', 'quote_count', 'reply_count', 'retweet_count']
user_public_metrics_keys = ['followers_count', 'following_count', 'listed_count', 'tweet_count']

def main():

    tweet_dfs = []
    user_dfs = []
    for f in tqdm(tweet_jsons):
        with open(f) as f:
            #空のjsonがあるため、try-except
            try:
                data = json.load(f)
            except:
                continue

            tweet_df = pd.DataFrame(data['data'])
            user_df = pd.DataFrame(data['includes']['users'])

            for k in tweet_public_metrics_keys:
                tweet_df[k]=tweet_df.apply(lambda x: x['public_metrics'][k] , axis=1)
                tweet_dfs.append(tweet_df)
            tweet_df.drop('public_metrics', inplace=True,axis=1)
            
            for k in user_public_metrics_keys:
                user_df[k]=user_df.apply(lambda x: x['public_metrics'][k] , axis=1)
                user_dfs.append(user_df)
            user_df.drop('public_metrics', inplace=True,axis=1)

    tweet_df = pd.concat(tweet_dfs)
    user_df = pd.concat(user_dfs)

    ### setting ###
    output_dir=os.path.dirname(__file__) + '/transform_data'
    os.makedirs(output_dir, exist_ok=True)
    ###############

    #pickle
    tweet_df.to_pickle(f'{output_dir}/tweet.pkl')
    user_df.to_pickle(f'{output_dir}/user.pkl')

    #csv
    tweet_df.to_csv(f'{output_dir}/tweet.csv', index=False)
    user_df.to_csv(f'{output_dir}/user.csv', index=False)

if __name__ == '__main__' :
    main()
            
        