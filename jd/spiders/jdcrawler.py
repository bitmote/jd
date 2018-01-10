# -*- coding: utf-8 -*-
import scrapy
import json
import xlwt


class JdcrawlerSpider(scrapy.Spider):
    name = 'jdcrawler'
    allowed_domains = ['www.jd.com']
    start_urls = []
    postfix = '&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main'
    prefix = 'http://list.jd.com/list.html?cat=5272,5307&page='
    base_url = prefix + str(1) + postfix
    json_url = 'http://cread.jd.com/readask/canReadForJSONP.action?my=ebook3&bookIds='
    start_urls.append(base_url)
    query_json = False
    page_num = 2
    vip_read = {}
    book_info = {}
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet(u'fluentread')
    sheet.write(0, 0, u'书名')
    sheet.write(0, 1, u'网址')

    def parse(self, response):
        #print response.text
        self.query_json = False
        book_items = response.xpath('//li[@class="gl-item"]')
        print len(book_items)
        book_strs = ''
        #是否是畅读通过ajax动态加载
        for item in book_items:
            book_id = item.xpath('./div/@data-sku').extract_first()
            book_name = item.xpath('./div/div[3]/a/em/text()').extract_first()
            book_url = item.xpath('./div/div[3]/a/@href').extract_first()
            book_url = 'http:' + book_url
            tup = (book_name,book_url)
            # print book_name
            # print book_url
            #print book_title
            # print book_id
            self.book_info[book_id] = tup
            book_strs += book_id + ','
        book_strs = book_strs[:-1]
        print book_strs
        book_url = self.json_url + book_strs
        if self.query_json == False:
            yield scrapy.Request(book_url,callback=self.query,dont_filter=True)
        # print 'query json',self.query_json
    def query(self,response):
        self.query_json = True
        # print 'in query method query json is true'
        #http://cread.jd.com/read/startRead.action?bookId=30353151&readType=0  畅读地址
        json_text = json.loads(response.text)
        #print json_text
        #print json_text['List']
        json_list = json_text['List']
        for i in range(len(json_list)):
            if json_list[i]['isFluentRead'] == True:
                book_sku = str(json_list[i]['wareId'])
                print 'is fluentread ',book_sku
                self.vip_read[book_sku] = True
        if self.page_num >= 128:
            print self.vip_read
            print self.book_info
            for book_sku in self.book_info.keys():
                if not self.vip_read.has_key(book_sku):
                    self.book_info.pop(book_sku)
            row_num = 0
            for key in self.book_info:
                row_num += 1
                self.sheet.write(row_num,0,self.book_info[key][0])
                self.sheet.write(row_num,1,self.book_info[key][1])
                #print self.book_info[key][0],self.book_info[key][1]
            self.wbk.save('fluentread.xls')
        if self.query_json == True and self.page_num <=127:
            base_url = self.prefix + str(self.page_num) + self.postfix
            print 'next page    ',self.page_num
            self.page_num += 1
            yield scrapy.Request(base_url,callback=self.parse,dont_filter=True)
