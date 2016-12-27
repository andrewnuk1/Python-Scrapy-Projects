import scrapy
import re

from CompaniesHouse.items import CompanieshouseItem

class CompaniesHouseSpider(scrapy.Spider):
    name = "companieshouse"
    allowed_domains = ["companieshouse.gov.uk"]

    # choice of LLPs or Companies to scrap
    # companieshousenumbers.txt is a file that holds a list of Companies House Numbers
    while True:
        to_do = raw_input("Enter 1 for LLPs or 2 for Companies  ")
        if to_do == "1":
            companynumbers = ["OC361003"] #LLps
            break
        elif to_do == "2":
            with open("companieshousenumbers.txt") as f:
                companynumbers = [x.strip('\n') for x in f.readlines()]
            break

    # build a list of urls to scrap from a list of company numbers    
    start_urls = []
    for a in range(len(companynumbers)):
        start_urls.append("https://beta.companieshouse.gov.uk/company/%s/officers" %companynumbers[a])

    def parse(self, response):

        def to_list(xpath):
            return [v.strip() for v in xpath.extract()]

        for count in range(0,100):
            for sel in response.xpath('//*[@id="content-container"]'):
                companys = to_list(sel.xpath('//*[@id="company-name"]/text()'))
                string1 = "officer-name-" + str(count)
                names = to_list(sel.xpath('//*[@id="{}"]/a/text()'.format(string1)))
                namerefs = sel.xpath('//*[@id="{}"]/a/@href'.format(string1)).re(r'(?<=/officers/).*?(?=/appointments)')
                namerefs = [nameref.strip() for nameref in namerefs]
                string2 = "officer-status-tag-" + str(count)
                statuss = to_list(sel.xpath('//*[@id="{}"]/text()'.format(string2)))
                string3 = "officer-role-" + str(count)
                roles = to_list(sel.xpath('//*[@id="{}"]/text()'.format(string3)))
                
                # not every "person" has a date of birth.  i.e. a company may be a "director", so give "n/a" where no date of birth exists
                string4 = "officer-date-of-birth-" + str(count)
                dateofbirths = to_list(sel.xpath('//*[@id="{}"]/text()'.format(string4)))
                if not dateofbirths:
                   dateofbirths = ["n/a"] 

                result = zip(companys, names, namerefs, roles, dateofbirths, statuss)
                for company, name, nameref, role, dateofbirth, status in result:
                   item = CompanieshouseItem()
                   item['company'] = company
                   item['name'] = name
                   item['nameref'] = "'" + nameref  # put a ' infront of the nameref value in case the value sits badly in a spreadsheet
                   item['status'] = status
                   item['role'] = role
                   item['dateofbirth'] = dateofbirth               
                   yield item

        # move to the next page, if applicable       
        next_page = response.xpath('//*[@class="pager"]/li/a[@class="page"][contains(., "Next")]/@href').extract()
        if next_page:
            next_href = next_page[0]
            next_page_url = "https://beta.companieshouse.gov.uk" + next_href
            request = scrapy.Request(url=next_page_url)
            yield request

