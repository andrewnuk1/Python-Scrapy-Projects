import scrapy

from justeat.items import JusteatItem

class JusteatSpider(scrapy.Spider):
    name = "justeat"
    allowed_domains = ["just-eat.co.uk"]

    start_urls = ["http://www.just-eat.co.uk/takeaway"]

    def parse(self, response):
        for href in response.css("div.linkArchitectureLinks > div.collapsible > ul.links > li > a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)
            
    def parse_dir_contents(self, response):
        for sel in response.xpath('//*[@class="restaurants"]'):
            names = sel.xpath('//*[@class="details"]/h2/text()').extract()
            names = [name.strip() for name in names]
            addresses = sel.xpath('//*[@class="address"]/text()').extract()
            addresses = [address.strip() for address in addresses]
            result = zip(names, addresses)
            for name, address in result:
                item = JusteatItem()
                item['name'] = name
                item['address'] = address
                yield item
