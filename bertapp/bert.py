from pathlib import Path

import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, Dataset

import transformers
from transformers import AutoConfig, AutoModel, AutoTokenizer

class TweetLikePredModel(nn.Module):
    def __init__(
        self
    ):
        #継承元のinitを使用
        super().__init__()

        #config
        self.model_config=AutoConfig.from_pretrained('cl-tohoku/bert-base-japanese-v2')

        #model
        self.model=AutoModel.from_pretrained('cl-tohoku/bert-base-japanese-v2')

        self.regressor = nn.Sequential(
            nn.Linear(self.model_config.hidden_size+2, 128),
            nn.LeakyReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1)
        )

    def forward(self, x):

        input_ids=x['input_ids']
        attention_mask=x['attention_mask']

        #その他特徴量
        tweet_hour=x['tweet_hour'].reshape(-1,1)
        followers_count=x['followers_count'].reshape(-1,1)
        
        out=self.model(input_ids,attention_mask)
        #pooler output = CLSトークンのemb層を抽出
        out = out[1]
        out =  torch.cat([out, tweet_hour, followers_count], dim=1)
        #batch*1で予測
        qa_logits=self.regressor(out)

        return qa_logits
