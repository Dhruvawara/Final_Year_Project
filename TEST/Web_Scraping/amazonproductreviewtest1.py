from amazon_product_review_scraper import amazon_product_review_scraper
import pandas
# https://www.amazon.in/dp/B089MTVYZF?pf_rd_r=A0AGR7CYW8WHNZ47RNXJ&pf_rd_p=acf65a9b-7d53-4b4d-a0c4-ae0e12e8f97c
review_scraper = amazon_product_review_scraper(
    amazon_site="amazon.in", product_asin="B08VWTS77G")
reviews_df,p_title,p_image = review_scraper.scrape()

reviews_df['rating'] = reviews_df['rating'].str[:1].astype(int)
print(p_title)
print(p_image)
with open('./scraped_data.csv', 'w') as csv_file:
    reviews_df.to_csv('./scraped_data.csv', index=False)
