#! /usr/bin/env python3
import requests
import scrapy
import pandas as pd
import re
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.response import open_in_browser


# Web Crawler Class
class CNBCSpider(scrapy.Spider):
    name = 'CNBC_spider'
    
    def start_requests(self):
        
        url = 'https://www.cnbc.com/'
        yield scrapy.Request(url= url, callback= self.parse_front_page) 
    
    def parse_front_page(self, response):
        headlines = [x for x in response.css('a::attr(href)').extract() if 'cnbc.com/2020/' in x]

        for link in headlines:
            yield response.follow(url=link, callback= self.parse_article)
    
    def parse_article(self, response):
        
        # get article headline
        headline = response.css('h1.ArticleHeader-headline::text').extract()
        if headline != []:
            headlines.append(headline)
        
        # get article dates
        date = response.css('div.ArticleHeader-time > time::text').extract()
        if date != []:
            dates.append(date) 
        
        # get article description
        # description = response.css('ul')
        # descriptions.append(description)


# initiate arrays to store data from the web crawler 
headlines, descriptions, dates = [], [], []



# Running the Spider 

# initiate a crawler process
process = CrawlerProcess()
    
# tell the process which spider to use
process.crawl(CNBCSpider)

# start the crawling process
process.start()


# parse Dates and Headlines
parsed_dates = [x[0].split(',')[1].strip() for x in dates]
parsed_headlines = [x[0] for x in headlines]

# build a df out of new scraped data 
df = pd.DataFrame(data={'publish_date':parsed_dates,
                        'headline':parsed_headlines})
# convert date column in datetime objects
df['publish_date'] = pd.to_datetime(df['publish_date'],infer_datetime_format=True)

# set the date column as the df index
df.set_index('publish_date',inplace = True)

# read old data df
df_old = pd.read_csv('data/cnbc_news.csv',parse_dates=['publish_date'], index_col='publish_date')

# concat new df to old df
combined_df = pd.concat([df_old,df], axis=0)

# remove duplicate headlines if they exist
combined_df.drop_duplicates(subset ="headline", keep = 'last', inplace = True) 

# sort df by date
combined_df.sort_values(by='publish_date', inplace=True)

# export file back to .CSV
combined_df.to_csv('data/cnbc_news.csv')


# read in and check new combined dataset from wsi_news.csv 
full_df = pd.read_csv('data/cnbc_news.csv',parse_dates=['publish_date'], index_col='publish_date')
print(full_df)
