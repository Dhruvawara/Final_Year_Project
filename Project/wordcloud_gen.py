import os
import pathlib
from flask import wrappers
from matplotlib import pyplot as plt
from wordcloud import WordCloud as wordcloud


def generate_wordcloud(data, title):
        wc = wordcloud(width=400, height=330, max_words=150,
                       background_color='white'). generate_from_frequencies(data)
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.title('\n'.join(wrappers(title, 60)), fontsize=13)
        # plt.show()
        if pathlib.exists('wordcloud.png'):
            os.remove('wordcloud.png')
        # wc.to_file('wordcloud.png')
        # return plt,wc
        # plt.savefig('wordcloud.png', format='png', dpi=500)
