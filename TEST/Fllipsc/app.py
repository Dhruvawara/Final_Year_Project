from flask import Flask, render_template, request
import requests
import flipkartscrapper
import seaborn as sns
import numpy as np
import os
import os.path
from os import path
from bs4 import BeautifulSoup
import pandas as pd
# For visualizations
import matplotlib.pyplot as plt
# For regular expressions
import re
# For handling string
import string
app = Flask(__name__)
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.106 Safari/537.36',
           'referrer': 'https://flipkart.com'
           }


@app.route('/')
def index():
    if path.exists('./scraped_data.csv'):
        os.remove('./scrapped_data.csv')
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url')
    # path = os.getcwd()
    #
    # print(path)
    if 'flipkart' in url:
        product_title = str(flipkartscrapper.flipscrapper(url))
    page = requests.get(url, headers=headers, timeout=2)
    soup = BeautifulSoup(page.text, 'html.parser')
    total_reviews = soup.find('span', attrs={'class': '_2_R_DZ'}).text
    

    df = pd.read_csv('./scrapped_data.csv')
    df = df[['Rating', 'Review']]  # getting required columns
    df['cleaned'] = df['Review'].apply(lambda x: x.lower())  # to lower letter
    df.isnull().sum()  # to check null values
    df.dropna(inplace=True)  # to remove null values if there
    df.isnull().sum()
    df['cleaned'] = df['cleaned'].apply(lambda x: re.sub(
        '\w*\d\w*', '', x))  # remove digits in data
    df['cleaned'] = df['cleaned'].apply(
        lambda x: re.sub('[%s]' % re.escape(string.punctuation), '', x))  # Remove Punctuations
    df['cleaned'] = df['cleaned'].apply(
        lambda x: re.sub(' +', ' ', x))  # Removing extra spaces
    # stopwords removal and lemmatization
    # Importing spacy
    import spacy
    # Loading model
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    # Lemmatization with stopwords removal
    df['lemmatized'] = df['cleaned'].apply(
        lambda x: ' '.join([token.lemma_ for token in list(nlp(x)) if (token.is_stop == False)]))

    # keeping reqired columns because the abbove cell appends extera columns
    df = df[['Rating', 'lemmatized']]
    df_new = df.rename(columns={'lemmatized': 'Review'})
    df = df_new
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    sent = SentimentIntensityAnalyzer()
    sentiment_dict = []
    for i in range(0, len(df)):
        sentiment_dict.append(sent.polarity_scores(df.iloc[i, 1]))
    positive = []
    neutral = []
    negative = []
    compound = []
    for item in sentiment_dict:
        positive.append(item['pos'])
        neutral.append(item['neu'])
        negative.append(item['neg'])
        compound.append(item['compound'])
    sentiment_df = pd.DataFrame(list(zip(positive, neutral, negative, compound)),  columns=[
                                'Positive', 'Neutral', 'Negative', 'Compound'])
    df['Positive'] = sentiment_df['Positive']
    df['Negative'] = sentiment_df['Negative']
    df['Neutral'] = sentiment_df['Neutral']
    df['Compound'] = sentiment_df['Compound']
    df_temp = df[['Rating', 'Review']]
    df_temp = df_temp.assign(new="1")
    df_grouped = df_temp[['new', 'Review']].groupby(
        by='new').agg(lambda x: ' '.join(x))
    # Creating Document Term Matrix
    from sklearn.feature_extraction.text import CountVectorizer
    cv = CountVectorizer(analyzer='word')
    data = cv.fit_transform(df_grouped['Review'])
    df_dtm = pd.DataFrame(data.toarray(), columns=cv.get_feature_names())
    df_dtm.index = df_grouped.index
    # Importing wordcloud for plotting word clouds and textwrap for wrapping longer text
    from wordcloud import WordCloud
    from textwrap import wrap
    # Function for generating word clouds

    def generate_wordcloud(data, title):
        wc = WordCloud(width=400, height=330, max_words=150,
                       background_color='white'). generate_from_frequencies(data)
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.title('\n'.join(wrap(title, 60)), fontsize=13)
        plt.show()
        if path.exists('./static/wordcloud.jpg'):
            os.remove('./static/wordcloud.jpg')
        wc.to_file("./static/wordcloud.jpg")
    # Transposing document term matrix
    df_dtm = df_dtm.transpose()
    # Plotting word cloud for each product
    for index, product in enumerate(df_dtm.columns):
        generate_wordcloud(df_dtm[product], product)
    highest_polarity = pd.DataFrame(columns=['Reviews'])
    lowest_polarity = pd.DataFrame(columns=['Reviews'])

    from textblob import TextBlob
    df['polarity'] = df['Review'].apply(
        lambda x: TextBlob(x).sentiment.polarity)
    for index, Review in enumerate(df.iloc[df['polarity'].sort_values(ascending=False)[:3].index]['Review']):
        highest_polarity = highest_polarity.append(
            {'Reviews': str(Review)}, ignore_index=True)

    for index, Review in enumerate(df.iloc[df['polarity'].sort_values(ascending=True)[:3].index]['Review']):
        lowest_polarity = lowest_polarity.append(
            {'Reviews': str(Review)}, ignore_index=True)
    # print('the highest: ', highest_polarity)
    # # print('the lowest: ', lowest_polarity)
    #
    # return render_template('process.html',title=product_title,tables=[highest_polarity.to_html(classes='data', index=False)],titles=highest_polarity.columns.values,total_reviews=total_reviews, pos = str(df['Positive'].mean() * 10)[0:3],
    #                        neg= str(df['Neutral'].mean() * 10)[0:3], neutral=str(df['Negative'].mean() * 10)[0:3])
    if float(df['Positive'].mean() * 10) > 6:
        verdict = 'This product is highly recommended!!!'
    elif float(df['Negative'].mean() * 10) < 0:
        verdict = 'This product is not recommended!'
    else:
        verdict = 'This product is recommended'
    return render_template('process.html', title=product_title, row_data=list(highest_polarity.values.tolist()), row2_data=list(lowest_polarity.values.tolist()), titles=highest_polarity.columns.values, total_reviews=total_reviews, pos=str(df['Positive'].mean() * 10)[0:3], neg=str(df['Neutral'].mean() * 10)[0:3], neutral=str(df['Negative'].mean() * 10)[0:3], verdict=verdict)


if __name__ == '__main__':
    app.run(debug=True)
