import scrapy
import requests
import re
import os
import shutil


class fbo_spider(scrapy.Spider):
    name = "fbo-crawler"

    save_path = "" 
    current_url = "" 
    # file containing urls to crawl is passed in from command line
    # > scrapy crawl fbo-crawler -a filename= ***FILE_LOCATION***
    def __init__(self, filename=None):
        self.save_path = ""
        self.current_url = ""
        if filename:
            with open(filename, 'r') as r:
                self.start_urls = r.readlines()
                

    def parse(self, response):  
        self.current_url = response.request.meta['redirect_urls'][0]
        length = len(response.xpath("//*[@class='pkglist']/dd/a").getall())
        if length == 0:
            self.save_path = "none"
        else:
            self.crawl(response)
        self.writeLocation(self.current_url, self.save_path)


    def crawl(self, response):
        for link in response.xpath("//*[@class='pkglist']/dd/a"):
            relative_url = link.xpath(".//@href").extract_first()
            self.getSolicitation(response)
            if not os.path.exists(self.save_path):
                os.mkdir(self.save_path)
            absolute_url = self.getAbsoluteUrl(relative_url)
            self.makeRequest(absolute_url)   


    def getSolicitation(self, response):
        solic_num = response.xpath("//*[@class='sol-num']/text()").get()
        solic_num = solic_num.split("Solicitation Number: ",1)[1] 
        self.save_path = "***LCOATION TO SAVE***" + solic_num 


    def getAbsoluteUrl(self, relative_url):
        base_url = "https://www.fbo.gov" 
        # ex: https://www.fbo.gov + /utils/view?id=921ca3f6f2ae471ab579075b8dc37afb
        if "https" in relative_url:
            absolute_url = relative_url
        else:
            absolute_url = base_url + relative_url 
        return absolute_url


    def makeRequest(self, absolute_url):
        r = requests.get(absolute_url)
        d = r.headers['content-disposition']
        file_download = re.findall("filename=(.+)", d)
        for file in file_download:
            writeFile = self.save_path + "/" + file.strip('\"')
            with open(writeFile, 'wb') as w: #writes to external drive
                w.write(r.content)


    # example file entry: URL + "\t" + location saved
    # https://www.fbo.gov/utils/view?id=921ca3f6afb     C:/SAVE_LOCATION
    def writeLocation(self, current_url, save_path):
        output_file = "**LOCATION TO WRITE A FILE CONTAINING PARSED URLs AND LOCATION OF FILES"
        if not os.path.exists(output_file):
            with open(output_file, 'w') as f:
                f.write(current_url + "     " + save_path + '\n')
        else:
            with open(output_file, 'a') as f: #writes to external drive
                f.writelines(current_url + "     " + save_path + '\n')