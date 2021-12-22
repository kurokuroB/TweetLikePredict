from django import forms

class TweetForm(forms.Form):
    text = forms.CharField(max_length=192, label= '「忘年会」という単語を含むツイートを記入', \
        widget=forms.Textarea(attrs={'rows':5, 'cols':80}))

    tweet_hour=forms.IntegerField(label= 'ツイート予定時間')
    followers_count=forms.IntegerField(label= 'フォロワー数')