#Process file
echo 'Crawling Data'
cd ./crawl
sh ./crawl.sh
echo 'Done Crawling'
echo 'Parsing Data'
cd ../
cd parse
sh ./parse.sh
echo 'Done Parsing Data'
echo 'Loading Data'
cd ../
cd load
sh ./load.sh
echo 'Done Loading Data'
cd ../
