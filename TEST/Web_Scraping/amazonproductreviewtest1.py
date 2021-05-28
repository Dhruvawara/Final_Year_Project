from amazon_product_review_scraper import amazon_product_review_scraper
# https://www.amazon.in/dp/B089MTVYZF?pf_rd_r=A0AGR7CYW8WHNZ47RNXJ&pf_rd_p=acf65a9b-7d53-4b4d-a0c4-ae0e12e8f97c
review_scraper = amazon_product_review_scraper(amazon_site="amazon.in", product_asin="B08VWTS77G")
reviews_df = review_scraper.scrape()
print(reviews_df)
