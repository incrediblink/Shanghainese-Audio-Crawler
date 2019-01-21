import scrapy
import csv
import os
from .page_spider import PageSpider

class MainSpider(scrapy.Spider):
  name = 'main'

  def start_requests(self):
    database = 'audio_spider/data/database.csv'
    if os.path.exists(database):
      os.remove(database)

    url = 'http://shh.dict.cn'
    yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    for category in response.css('.obox-c.fydl.fc80 dl'):
      for url in category.css('a::attr(href)'):
        yield scrapy.Request(url='http://shh.dict.cn' + url.extract(), callback=self.send)

  def send(self, response):
    lastPage = response.css('#pager a::attr(href)')[-1].extract()
    max = int(lastPage.split('/')[-1])
    for i in range(1, max):
      url = response.url + '/' + str(i)
      yield scrapy.Request(url=url, callback=self.getAudio)

  def getAudio(self, response):
    for item in response.css('.o_mm .mbox-c li'):
      id = item.css('p img::attr(audio)').extract()[0]
      shanghainese = item.css('p a::text').extract()[0]
      mandarin = item.css('p')[1].css('::text').extract()[0]
      mandarin = mandarin[slice(4, len(mandarin), 1)]
      yield scrapy.Request(url='http://audio.dict.cn/mp3.php?q=' + id, callback=self.store)

      with open('audio_spider/data/database.csv', mode='a') as db:
        fieldnames = ['id', 'shanghainese', 'mandarin', 'path']
        db_writer = csv.DictWriter(db, fieldnames=fieldnames)
        db_writer.writerow({
          'id': id,
          'shanghainese': shanghainese,
          'mandarin': mandarin,
          'path': 'audio_spider/data/' + id + '.mp3'
        })
        db.close()

  def store(self, response):
    filename = 'audio_spider/data/' + response.url.split('=')[-1] + '.mp3'
    with open(filename, 'wb') as f:
      f.write(response.body)
      f.close()
