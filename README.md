# Obtaining microbial growth temperatures
The scrips in this repository were used to obtain growth temperatures for microbes deposited in culture collection centers. 
"Correlating enzyme annotations with a large set of microbial growth temperatures reveals metabolic adaptations to growth at diverse temperatures, my Mart Engqvist (https://doi.org/10.1101/271569 ).

# A note on the the code
Running this code will result in the downloading of VERY MANY html pages, on the order of several 100.000. They may therefore intermittenly fail and will need to be re-started. Organism names and temperatures are then mined form these pages. The research study was conducted in 2016 and 2017 and the scripts worked well at that point. I will make no effort to keep them up to date with any changes in the html page format carried out by the culture collection centers. As a result, I cannot guarantee that the scripts will actually work when you run them. I post the scripts here with hope that they may be of some use in future research projects.

# A note on credentials
The BacDive database requires pre-registration to use their API. For the BacDive code to work you will need to enter your username and password in the "credentials.txt" file. Additionally, web queries are made against the NCBI taxonomy database. As a curtesy to them you should enter your email address in the "credantials.txt" file. That way, if you perform too many queries too fast or at the wrong time of day they will give you a warning before blocking your IP address.

# Running the code
The code relies on Python version 2.7. In addition to this the wget command is used to download some of the html resources, so you will need to run this in a UNIX system. In principle the entire analysis can be completed by running the three scripts in the base folder in order.

```
>>> python 1_download_and_parse_all_databases_and_match_taxid.py
>>> python 2_clean_data_and_get_lineages.py
>>> python 3_fuse_data_and_output_results.py
```


