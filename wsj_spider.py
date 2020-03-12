#! /usr/bin/env python3
import requests
import scrapy
import pandas as pd
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.response import open_in_browser
# ***** NOTE: you MUST restart the kernal everytime you want to run the spider *****

# Web Crawler Class
class WSJSpider(scrapy.Spider):
    name = 'WSJ_spider'
    
    def start_requests(self):
        
        url = 'https://www.wsj.com/'
        yield scrapy.Request(url= url, callback= self.login) 
    
    def login(self, response):
        return scrapy.FormRequest.from_response(response,
            formdata={'username': 'michaelblau@wustl.edu', 'password': 'Magic1998'},
            callback=self.after_login)
    
    def after_login(self, response):
        headlines_links = response.css('h3.WSJTheme--headline--19_2KfxG > a::attr(href)').extract()
        
        for link in headlines_links:
            if 'wsj' in link:
                yield response.follow(url=link, callback= self.parse_article)
    
    def parse_article(self, response):
        
        # get article headline
        headline = response.css('h1.wsj-article-headline::text').extract()
        if len(headline) == 0:
            headline = response.css('h1.bigTop__hed::text').extract()
        headline = headline[0].strip()
        headlines.append(headline)
        
        # get article description
        description = response.css('h2.sub-head::text').extract()
        if len(description) == 0:
            description = None
            descriptions.append(description)
        else:
            descriptions.append(description[0])
        
        # get article date
        date = response.css('time.article__timestamp::text').extract()
    
        if len(date)==0:
            open_in_browser(response)
            date = None
            article_dates.append(date)
        else:
            article_dates.append(date[0].strip())
            
        # get article authors
        article_authors.append(response.css('ul.author-info > div.info-name::text').extract())  


# initiate arrays to store data from the web crawler 
headlines, descriptions, article_authors , article_dates, descriptions = [], [], [], [], []


# Running the Spider 

# initiate a crawler process
process = CrawlerProcess()
    
# tell the process which spider to use
process.crawl(WSJSpider)

# start the crawling process
process.start()


def convertToDatetime(s):
    """
    Input
        String: raw date text from a WSJ article
    Output
        Datetime object
    """
    if isinstance(s,str):
        # use a regex to parse out date if it exists, otherwise return a None value
        pattern = re.compile(r'([\w]{3,10})\.? ([\d]{1,2}), ([\d]{4})')
        match = pattern.search(s)
        if match is not None:
            print(match.groups())
            group = match.groups()
            if len(group) == 3:
                return '/'.join(group)
            else:
                return '/'.join(group[1:])
        else:
            return None
    else:
        return None


# build a df out of new scraped data 
df = pd.DataFrame(data={'publish_date':article_dates,
                        'headline':headlines,
                        'description': descriptions})
# convert date column in datetime objects
df['publish_date'] = df['publish_date'].apply(lambda s: convertToDatetime(s))
df['publish_date'] = pd.to_datetime(df['publish_date'],infer_datetime_format=True)

# set the date column as the df index
df.set_index('publish_date',inplace = True)

# read old data df
df_old = pd.read_csv('wsj_news.csv',parse_dates=['publish_date'], index_col='publish_date')

# concat new df to old df
combined_df = pd.concat([df_old,df], axis=0)

# remove duplicate headlines if they exist
combined_df.drop_duplicates(subset ="headline", keep = 'last', inplace = True) 

# sort df by date
combined_df.sort_values(by='publish_date', inplace=True)

# export file back to .CSV
combined_df.to_csv('wsj_news.csv')

# read in and check new combined dataset from wsi_news.csv 
full_df = pd.read_csv('wsj_news.csv',parse_dates=['publish_date'], index_col='publish_date')
print(full_df)
