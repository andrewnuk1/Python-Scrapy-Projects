import scrapy
import re

from CompaniesHouse.items import CompanieshouseItem

class CompaniesHouseSpider(scrapy.Spider):
    name = "companieshouse"
    allowed_domains = ["companieshouse.gov.uk"]

    # choice of LLPs or Companies to scrap
    while True:
        to_do = raw_input("Enter 1 for LLPs or 2 for Companies  ")
        if to_do == "1":
            companynumbers = ["OC361003"] #LLps
            break
        elif to_do == "2":
            companynumbers = ["05149111","SC082015","SC126524","07123187","SC177553","06764335","SC001731","08998697","01675285","05525751","00435820",
    "03675683","09349441","01885586","09439967","02937296","00395826","00026351","SC005653","00053688","09763575","01372603",
    "01480047","05172586","07811410","03625199","00519057","05145685","00306718","02685806","00028203","05604923","00814103",
    "02670500","SC226712","00235481","07145051","09002747","03782379","08816954","05212407","00034871","01190238","00520241",
    "02714781","05145017","00030470","03110569","09878920","01074383","06800600","09595911","00305105","03162897","05448421",
    "03369634","01819699","04569346","03899848","03853545","05562053","04708277","SC052844","06885579","00647788","03299608",
    "06269098","05444653","07064312","00954730","07784342","05432915","07133583","02638812","03234176","SC013958","SC157176",
    "00012901","04992207","00836539","02972325","02100855","02886378","00125575","00596137","08318092","02614349","00024511",
    "00502851","04457314","00040932","05605371","09635183","02150950","BR016747","07409699","00671474","02837811","05777693",
    "02648297","02128710","00974568","09760850","04677092","00714275","00609782","09237894","04886072","02234775","06018973",
    "05938778","03633621","04204490","07080503","01709784","00211475","01679424","01888425","05975300","04401816","00015543",
    "02618994","02915926","08568957","06150195","06947854","05180783","02442580","02708030","00566221","01477482","07124797",
    "08172396","05100353","00031461","06622199","00432989","00020537","06419578","03004377","04551498","SC019230","06160943",
    "00236964","00286773","SC006705","02590560","10221027","10013770","07712220","08717287","07098618","07312896","08805459",
    "03310225","02336032","03581541","04478861","02366640","03156676","SC074582","08139825","SC074582","04597286","08885072",
    "05252074","03224867","07703858","06059130","00019457","04586941","03140769","01000403","FC024374","02877315","01106260",
    "05393279","SC030343","06426485","02129188","00578327","02578443","04726380","08804263","02122174","SC001651","SC007058",
    "01087016","00282772","02048608","01999238","07240248","00998314","01377658","02174990","09608658","02025003","00596337",
    "09084066","06035106","05735966","00349201","SC100764","07063562","03066856","00098381","07105891","00076535","03393836",
    "03263464","00214601","SC118022","08506871","06091951","00084492","00824821","08215888","03904126","03919249","06842660",
    "08445432","LP008281","02830397","03199160","03418970","04740415","08217766","02793780","03087587","SC002934","05202036",
    "04212563","00101625","FC026418","SC036219","09405653","02041612","03023689","09005884"
    ] # Companies
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
