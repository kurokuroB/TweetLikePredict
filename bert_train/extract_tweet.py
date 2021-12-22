import os
import requests
import time
import json
import datetime
from box import Box

#現在時刻
dt_now = datetime.datetime.now()


config={
    'bearer_token':'<bearer_tokenを記載>'

    # 検索ワード  e.g. query = "テスト" / query = "テスト OR test"
    # OR 検索　AND検索　-検索　などしたい場合はそのように書く
    'query': "忘年会",

    'tweet_fields': ['created_at','public_metrics'] ,

    'options': {
        'max_results': '100',
        #defaultは7日前
        'start_time': (dt_now-datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        #defaultは2日前。ある程度時間が経過しないと、いいね数が確定しないため
        'end_time': (dt_now-datetime.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    },

    #expansionsに対応するfieldを辞書で格納
    'expansions': {'author_id':{
        'user.fields':['created_at','public_metrics']
        }}

}

config=Box(config)


#取得したい項目をパラメータに設定して、URLを作成している。
def create_url(query, tweet_fields, options, expansions):
    if len(tweet_fields)>=1:
        formatted_tweet_fields = '&tweet.fields=' + ','.join(tweet_fields)
    else:
         formatted_tweet_fields = ""

    if len(options)>=1:
        formatted_option_fields = []
        for k, v in options.items():
            formatted_option_field=f'{k}=' + f'{v}'
            formatted_option_fields.append(formatted_option_field)
        formatted_option_fields = '&'+'&'.join(formatted_option_fields)
    else:
         formatted_option_fields = ''

    expansions_key=list(expansions.keys())
    if len(expansions_key)>=1:
        formatted_expansions = '&expansions=' + ','.join(expansions_key)

        #対応するfieldを整理
        formatted_attr_fields=[]
        for key in expansions_key:
            attr_fields=expansions[key]
            for k, v in attr_fields.items():
                formatted_attr_field=f'{k}=' + ','.join(v)
                formatted_attr_fields.append(formatted_attr_field)

        formatted_attr_fields='&'+'&'.join(formatted_attr_fields)

    else:
         formatted_expansions = ''
         formatted_attr_fields = ''
         
    url = f'https://api.twitter.com/2/tweets/search/recent?query={query}{formatted_tweet_fields}{formatted_option_fields}{formatted_expansions}{formatted_attr_fields}'
    return url

#リクエスト用のheader 
def create_headers(bearer_token):
    headers = {'Authorization': f'Bearer {bearer_token}'}
    return headers

def main():

    # setting
    output_dir=os.path.dirname(__file__) + '/output'
    os.makedirs(output_dir, exist_ok=True)

    BEARER_TOKEN = config.bearer_token
    query = config.query
    tweet_fields = config.tweet_fields
    options = config.options
    expansions = config.expansions

    origin_url = create_url(query, tweet_fields, options, expansions)
    headers = create_headers(BEARER_TOKEN)
    
    #リクエスト実行。最初だけ、origin_url
    url=origin_url
    while True:
        
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            #参考：https://toricor.hatenablog.com/entry/2016/01/16/160406
            with open(f'{output_dir}/{datetime.datetime.now()}.json', 'w') as f:
                json.dump(response.json(), f, indent=4, sort_keys=True, ensure_ascii=False)
            
            try:
                #もしも、next_tokenがあればそれに基づき、新しいurlを作成。
                next_token=response.json()['meta']['next_token']
                url=origin_url+'&next_token='+next_token

            #もしもnext_tokenがない（＝次がない場合、ループを抜ける）
            except:
                break
        
        else:
            #api制限にかかった場合、スリープする。
            time.sleep(15*60)
        

if __name__ == "__main__":
    main()