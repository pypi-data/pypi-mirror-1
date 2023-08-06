#There are two option of downloading data. 
#One is to use wget and specify exactly what you want to download by editing download_list.txt and running "sh download.sh" or use harvestman to crawl the webpage for you. You can edit sample harvestman xml or you can generate it yourself by running "harvestman --genconfig"

#Crawl Instructions for datahubgovdotnhtsarecall.
#Run harvestman:
harvestman -C harvestman-datahubgovdotnhtsarecall.xml  

#Run wget
#sh download.sh
