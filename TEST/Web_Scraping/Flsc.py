import requests
from bs4 import BeautifulSoup as bs
import re
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
macbook_reviews = []
for i in range(1):
    mac = []
    url = "https://www.flipkart.com/intex-oxiscan-pulse-oximeter-oxygen-saturation-monitor-heart-rate-spo2-levels-meter-led-display/product-reviews/itmbd2cc10bb14b8?pid=POXFV2AQN5F4X7M9&lid=LSTPOXFV2AQN5F4X7M99NWCJB&marketplace=FLIPKART&page=" + \
        str(i)
    response = requests.get(url)
    # creating soup object to iterate over the extracted content
    soup = bs(response.content, "html.parser")
    # Extracting the content under specific tags
    reviews = soup.findAll("div", attrs={"class", "t-ZTKy"})
    for i in range(len(reviews)):
        mac.append(reviews[i].text)
        macbook_reviews = macbook_reviews+mac
# here we saving the extracted data
with open("macbook.txt", "w", encoding='utf8') as output:
    output.write(str(macbook_reviews))


# os.getcwd()
# os.chdir("/content/chider")

# Joining all the reviews into single paragraph
mac_rev_string = " ".join(macbook_reviews)

# Removing unwanted symbols incase if exists
mac_rev_string = re.sub("[^A-Za-z" "]+", " ", mac_rev_string).lower()
mac_rev_string = re.sub("[0-9" "]+", " ", mac_rev_string)

# here we are splitting the words as individual string
mac_reviews_words = mac_rev_string.split(" ")

# removing the stop words
#stop_words = stopwords('english')


with open("stop.txt", "r") as sw:
    stopwords = sw.read()
temp = ["this", "is", "awsome", "Data", "Science"]
[i for i in temp if i not in "is"]
mac_reviews_words = [w for w in mac_reviews_words if not w in stopwords]
mac_rev_string = " ".join(mac_reviews_words)
# creating word cloud for all words
wordcloud_mac = WordCloud(background_color='black',
                          width=1800, height=1400).generate(mac_rev_string)
plt.imshow(wordcloud_mac)


with open("/content/positive-words.txt", "r") as pos:
    poswords = pos.read().split("\n")
    poswords = poswords[36:]

mac_pos_in_pos = " ".join([w for w in mac_reviews_words if w in poswords])
wordcloud_pos_in_pos = WordCloud(
    background_color='black',
    width=1800,
    height=1400
).generate(mac_pos_in_pos)
plt.imshow(wordcloud_pos_in_pos)

# here we get wordcloud of all postive words in reviews


with open("/content/negative-words.txt", "r", encoding="ISO-8859-1") as neg:
    negwords = neg.read().split("\n")
    negwords = negwords[37:]

# negative word cloud
# Choosing the only words which are present in negwords
mac_neg_in_neg = " ".join([w for w in mac_reviews_words if w in negwords])

wordcloud_neg_in_neg = WordCloud(
    background_color='black',
    width=1800,
    height=1400
).generate(mac_neg_in_neg)
plt.imshow(wordcloud_neg_in_neg)

# here we are getting the most repeated negative Wordcloud
