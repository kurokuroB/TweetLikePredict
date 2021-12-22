from pathlib import Path
import pickle
from django.shortcuts import render
from .forms import TweetForm
from .bert import TweetLikePredModel
import numpy as np
from sklearn.preprocessing import StandardScaler
import torch
from transformers import AutoTokenizer

#以下、デバッグでは重いので、いったんコメントアウト

#tokenizerの設定。
TOKENIZER=AutoTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-v2')

#標準化用のStandardScaler
SCALER_PATH=Path(__file__).parent / 'static' / 'standardscaler_for_tweetlikepred.pkl'

with open(SCALER_PATH,"rb") as f:
    SCALER=pickle.load(f)

#デバイス指定
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
#重みの指定
CHECKPOINT=Path(__file__).parent / 'static' / '1fold_best_loss.ckpt'
#model作成
MODEL=TweetLikePredModel()
MODEL.load_state_dict(torch.load(CHECKPOINT, map_location=torch.device(DEVICE))['state_dict'])

def inputfunc(request):
    params={'form': TweetForm()}
    return render(request, 'input.html', params)

def predictfunc(request):
    params = {'pred': None}
    
    if request.method == 'POST':
        text_ = request.POST['text']
        tweet_hour = request.POST['tweet_hour']
        followers_count = request.POST['followers_count']
        print(text_)

        #標準化
        num_features=np.array([tweet_hour,followers_count]).reshape(1,-1)
        std_output=SCALER.transform(num_features)
        tweet_hour,followers_count=std_output[0][0], std_output[0][1]

        #setup
        encode_text=TOKENIZER(
                        text=text_,
                        return_attention_mask=True,
                        truncation=True,
                        max_length=192,
                        padding='max_length'
                        )

        input_ids=encode_text['input_ids']
        attention_mask=encode_text['attention_mask']

        #2次元tensor化
        all_input={'input_ids': torch.tensor(input_ids).reshape(1,-1), 
           'attention_mask': torch.tensor(attention_mask).reshape(1,-1),
           'tweet_hour': torch.tensor([tweet_hour], dtype=torch.float).reshape(-1,1),
           'followers_count': torch.tensor([[followers_count]], dtype=torch.float).reshape(-1,1)}

        #推論
        #eval_mode
        MODEL.eval()
        with torch.no_grad():
            logit=MODEL(all_input)
            params['pred']=round(logit.item(),2)
        print(logit)

        return render(request, 'result.html', params)
