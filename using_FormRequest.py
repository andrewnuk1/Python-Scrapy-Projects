import scrapy
import sys

from scrapy.http import FormRequest, Request
from Howdens.items import HowdensItem

class howdensSpider(scrapy.Spider):
    name = "howdens"
    allowed_domains = ["www.howdens.com"]

    # read the file that has a list of google coordinates that are converted from postcodes
    with open("googlecoords.txt") as f:
        googlecoords = [x.strip('\n') for x in f.readlines()]

    # from the goole coordinates build the start URLs
    start_urls = []
    for a in range(len(googlecoords)):
        start_urls.append("https://www.howdens.com/process/searchLocationsNear.php?{}&distance=1000&units=MILES".format(googlecoords[a]))

    # cycle through 6 of the first relevant items returned in the text
    def parse(self, response):
        for sel in response.xpath('/html/body'):
            for i in range(0,6):
                try:
                    item = HowdensItem()
                    item['name'] =sel.xpath('.//text()').re(r'(?<="name":")(.*?)(?=","street")')[i]
                    item['street'] =sel.xpath('.//text()').re(r'(?<="street":")(.*?)(?=","town")')[i]
                    item['town'] = sel.xpath('.//text()').re(r'(?<="town":")(.*?)(?=","pc")')[i]
                    item['pc'] = sel.xpath('.//text()').re(r'(?<="pc":")(.*?)(?=","state")')[i]
                    yield item
                except IndexError:
                    pass