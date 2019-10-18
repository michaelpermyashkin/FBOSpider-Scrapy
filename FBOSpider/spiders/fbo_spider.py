import scrapy
import requests
import re
import os
import shutil

class fbo_spider(scrapy.Spider):
    name = "fbo-crawler"
    
    download_counter = 0 # file downloads counter
    save_path = "" # location where downloads are stored - built as url is crawled & files found
    current_url = "" # current url being crawled

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
        # if no attachments exist at URL - write URL to file with "none" as destination
        if length == 0:
            self.save_path = "none"
        # else - crawl page
        else:
            self.crawl(response)
    
        #write E:/ drive location of directory to url file on same line as corresponding url
        self.writeLocation(self.current_url, self.save_path)

        # prints completed URL and how many files were downloaded
        print(self.current_url+ " : " + str(self.download_counter))
        self.download_counter = 0


    # build absolute URL for download from href on page
    # makes request by calling makeRequest function
    def crawl(self, response):
        for link in response.xpath("//*[@class='pkglist']/dd/a"):
            relative_url = link.xpath(".//@href").extract_first()
            self.getSolicitation(response)
            if not os.path.exists(self.save_path):
                os.mkdir(self.save_path)

            # builds url for http request to download
            absolute_url = self.getAbsoluteUrl(relative_url)
            self.makeRequest(absolute_url)   


    # Scrapes listing page for Solicitation Number 
    # If Found - appends SolNum to save path as directory name
    def getSolicitation(self, response):
        # scrap page for Solicitation Number - files stored on drive in directory named with Solication Num
        solic_num = response.xpath("//*[@class='sol-num']/text()").get()
        solic_num = solic_num.split("Solicitation Number: ",1)[1] 
        self.save_path = "***LCOATION TO SAVE***" + solic_num 


    # Builds absolute URL for download based on href attribute
    def getAbsoluteUrl(self, relative_url):
        base_url = "https://www.fbo.gov" # base url used build url from href link 
        # ex: https://www.fbo.gov + /utils/view?id=921ca3f6f2ae471ab579075b8dc37afb
        if "https" in relative_url:
            # checks case where href url is not a relative link
            absolute_url = relative_url
        else:
            absolute_url = base_url + relative_url 

        return absolute_url


    # recieves absolute URL as param, makes request, downloads files and stores on drive
    def makeRequest(self, absolute_url):
        r = requests.get(absolute_url)
        d = r.headers['content-disposition']
        file_download = re.findall("filename=(.+)", d)
        for file in file_download:
            writeFile = self.save_path + "/" + file.strip('\"')
            with open(writeFile, 'wb') as w: #writes to external drive
                w.write(r.content)
            self.download_counter+=1


    # writes location of downloaded pdfs of Seagate
    def writeLocation(self, current_url, save_path):
        output_file = "**LOCATION TO WRITE A FILE CONTAINING PARSED URLs AND LOCATION OF FILES"
        if not os.path.exists(output_file):
            with open(output_file, 'w') as f: #writes to external drive
                f.write(current_url + "     " + save_path + '\n')
        else:
            with open(output_file, 'a') as f: #writes to external drive
                f.writelines(current_url + "     " + save_path + '\n')