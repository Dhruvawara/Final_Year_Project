from flask import Flask, render_template, request
import requests
import seaborn as sns
import numpy as np
import os
import os.path
from os import path
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
import string
from amazon_product_review_scraper import amazon_product_review_scraper
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
from textwrap import wrap
from textblob import TextBlob
import wordcloud_gen

app = Flask(__name__)


@app.route('/')
def index():
    if path.exists('scraped_data.csv'):
        os.remove('scraped_data.csv')
    return render_template('index.html', product='Product')


@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url')

    if 'amazon.in' in url:
        product_asin = url[url.find('dp/')+3: url.find('dp/')+13]
        # https://www.amazon.in/dp/0143453645/ref=s9_acsd_obs_hd_bw_b1RCrtn_c2_x_16_t?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-11&pf_rd_r=WYQGZ516Q1DNGHBM7RP5&pf_rd_t=101&pf_rd_p=3119490d-c041-5aa7-960c-2ad787501dff&pf_rd_i=1318161031

        review_scraper = amazon_product_review_scraper(
            amazon_site="amazon.in", product_asin=product_asin)
        reviews_df, p_title, p_image = review_scraper.scrape()

        reviews_df['rating'] = reviews_df['rating'].str[:1].astype(int)

        with open('scraped_data.csv', 'w') as csv_file:
            reviews_df.to_csv('scraped_data.csv', index=False)
    else:
        return '<script>alert("Only works with amazon.in");window.history.back();</script>'
    print(p_title, p_image)
    df = pd.read_csv('scraped_data.csv')
    no_of_reviews = len(df)
    df = df[['content', 'rating']]
    df['cleaned'] = df['content'].apply(lambda x: re.sub('\w*\d\w*', '', x))
    df['cleaned'] = df['cleaned'].apply(lambda x: re.sub(
        '[%s]' % re.escape(string.punctuation), '', x))  # Remove Punctuations
    df['cleaned'] = df['cleaned'].apply(lambda x: re.sub(' +', ' ', x))

    # python -m spacy download en_core_web_sm

    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    df['lemmatized'] = df['cleaned'].apply(lambda x: ' '.join(
        [token.lemma_ for token in list(nlp(x)) if (token.is_stop == False)]))

    df = df[['rating', 'lemmatized']]
    df_new = df.rename(columns={'lemmatized': 'content'})
    df = df_new

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
    print(df.columns)
    df_temp = df[['rating', 'content']]
    df_temp = df_temp.assign(new="1")

    df_grouped = df_temp[['new', 'content']].groupby(
        by='new').agg(lambda x: ' '.join(x))

    cv = CountVectorizer(analyzer='word')
    data = cv.fit_transform(df_grouped['content'])
    df_dtm = pd.DataFrame(data.toarray(), columns=cv.get_feature_names())
    df_dtm.index = df_grouped.index

    def generate_wordcloud(data, title):
        wc = WordCloud(width=400, height=330, max_words=150,
                       background_color='white'). generate_from_frequencies(data)
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.title('\n'.join(wrap(title, 60)), fontsize=13)
        # plt.show()
        if path.exists('Project/static/wordcloud.png'):
            os.remove('Project/static/wordcloud.png')
        # wc.to_file('wordcloud.png')
        # return plt,wc
        plt.savefig('Project/static/wordcloud.png', format='png', dpi=500)

    df_dtm = df_dtm.transpose()

    for index, product in enumerate(df_dtm.columns):
        generate_wordcloud(df_dtm[product], product)
        # wordcloud_gen.generate_wordcloud(df_dtm[product], product)

    highest_polarity = pd.DataFrame(columns=['content'])
    lowest_polarity = pd.DataFrame(columns=['content'])

    df['polarity'] = df['content'].apply(
        lambda x: TextBlob(x).sentiment.polarity)
    for index, Review in enumerate(df.iloc[df['polarity'].sort_values(ascending=False)[:3].index]['content']):
        highest_polarity = highest_polarity.append(
            {'content': str(Review)}, ignore_index=True)

    for index, Review in enumerate(df.iloc[df['polarity'].sort_values(ascending=True)[:3].index]['content']):
        lowest_polarity = lowest_polarity.append(
            {'content': str(Review)}, ignore_index=True)

    if float(df['Positive'].mean() * 10) > 6:
        verdict = 'This product is highly recommended!!!'
    elif float(df['Negative'].mean() * 10) < 0:
        verdict = 'This product is not recommended!'
    else:
        verdict = 'This product is recommended'

    return render_template('process.html', p_image=p_image, p_title=p_title, len_r=no_of_reviews, row_data=list(highest_polarity.values.tolist()), row2_data=list(lowest_polarity.values.tolist()), titles=highest_polarity.columns.values, total_reviews=len(df), pos=str(df['Positive'].mean() * 10)[0:3], neg=str(df['Neutral'].mean() * 10)[0:3], neutral=str(df['Negative'].mean() * 10)[0:3], verdict=verdict)


if __name__ == '__main__':
    app.run(debug=True)
