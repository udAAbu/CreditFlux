**Table of Contents** 
- [Installation](#installation) 
  - [Installing Python](#installing-python)
  - [Installing Prerequisites](#installing-prerequisites)
  - [Installing Chromedriver](#installing-chromedriver)
- [Intro](#intro)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Downloading Multiple CLO Files](#downloading-multiple-clo-files)
  - [Specifying Download Folder](#specifying-download-folder)
  - [Logging In](#logging-in)
  - [Windows Chromedriver](#windows-chromedriver)
- [ExtractDataPage](#extractdatapage)


## Installation

#### **Installing Python**

If you already have Python 3.x installed, you may skip this step. However, you should make sure that you have the correct version of Python installed. To check which version of Python you are running, open up Terminal (Mac OS) or Command Prompt (Windows) and type:

```
$ python --version
```

which will display which version you are on (e.g. `$ 3.6.0`). If doing so yields the old Python 2.7 version, you may have to use `python3` instead of `python`. Also check to make sure your version of `pip` is updated and corresponds to the version of Python that you are using. Type `pip --version` to see which version you are on. It should look something like `pip 20.0.1 from path/to/pip (python 3.6)` where `path/to/pip` corresponds to the filepath of wherever pip is located. 

If you do not have Python 3.x installed, download and install from here: 

https://www.python.org/downloads/

#### **Installing Prerequisites**

The following are the prerequisite packages that must be installed in order for the application to work:

```
decorator==4.4.1
et-xmlfile==1.0.1
jdcal==1.4.1
numpy==1.18.1
openpyxl==3.0.3
pandas==0.25.3
py==1.8.1
python-dateutil==2.8.1
pytz==2019.3
retry==0.9.2
selenium==3.141.0
six==1.14.0
tqdm==4.41.1
urllib3==1.25.8
xlrd==1.2.0
```
To install these packages, type

```
$ pip install -r requirements.txt
```

which will automatically download and install them. If any of the packages fail to download using `pip install -r requirements.txt`, you can try individually installing the ones that failed using `pip install NAME_OF_PACKAGE`.

#### **Installing Chromedriver**

The Chromedriver is an executable file that mimics an instance of Google Chrome. 

*To install it on Mac OS*, you need to copy the `chromedriver` file into `/usr/bin` or `/usr/local/bin`. This adds the chromedriver to the system's PATH, so that later on a Selenium Webdriver knows where to locate it. To add the file to PATH, open up Terminal while in the application folder and type:

```
$ cp chromedrivers/mac/chromedriver /usr/local/bin
```

*To install it on Windows*, you do not need to move/copy any files. Later on, you will need to give the filepath of the windows chromedriver file to the `ExtractDataPage` object so that the Webdriver can use it.

## Intro ##

The two problems of downloading files from https://cloi.creditflux.com/ExtractData are:

  1. Downloading files from multiple CLO deals is a time-consuming manual process.
  
  2. The excel files downloaded from the site have a 5000-line limit. In order to download all historical data for any particular CLO deal, one must download the excel data, see how far back the records go before hitting the 5000-line limit, then re-download starting from the the oldest record date. This process needs to be repeated until all historical data is downloaded, then the excel files must be stitched together and any overlapping data between the excel files must be trimmed so no duplicates arise from the stitching process (although the original data itself may contain duplicates).
  
The first problem is solved using the Python implementation of Selenium Webdriver. Selenium Webdriver mimics an instance of a web browser. It can connect to a website and interact with its elements, clicking on links, selecting dropdown choices, filling in fields. Anything that can be done by a human through a web browser and a mouse and keyboard, can be done by the Selenium Webdriver. Once the Selenium Webdriver has been set up, one simply needs to write a Python script that automatically fills in the selections and choices on the creditflux website and clicks the download button.

The second problem is solved using the Python package `pandas`. `pandas` is a data analysis package that allows one to read, write, and save excel sheets. By downloading the excel sheets and checking if it hits the 5000-line limit, we can quickly go back and redownload any missing data and stitch the excel sheets together with a Python script that uses `pandas`. 

## Usage ##


The page from which we download the CLO excel data is encapsulated in the ExtractDataPage class. ExtractDataPage is a class which contains an instance of the Selenium Webdriver (running off of chromedriver). It also contains several Webdriver elements which represent some of the elements on the webpage. These elements can be interacted with using different ExtractDataPage object methods that can choose an option from the dropdown selection, enter the name of a CLO deal into the corresponding field, or download the excel data from the website. 

#### Quick Start #####

The quickest way to download excel sheets from the site is within Python's interactive mode. While inside the application folder, open up Terminal or Command Prompt and type `python -i main.py`

```
$ python -i main.py
>>> 
```

First create an ExtractDataPage object:

```
>>> page = ExtractDataPage()
Connecting to https://cloi.creditflux.com/ExtractData...
Loading cookies...
Identifying filter elements...
>>>
```

To download all the results for a given CLO, invoke the `download()` method like so:

```
>>> page.download('Aurium CLO II')
Downloading Holdings...
Downloading Test Results...
Downloading Tranches...
Downloading Distributions...
Downloading Purchase/sale...
>>> 
```

By default, calling `page.download('CLO_DEAL_NAME')` will download *all* the data for that CLO, including Test Results, Tranches, Distributions, Holdings, and Purchase/sale, from the earliest record date to the present date, and the output is a single excel file with a separate sheet for each of the previously mentioned categories. The excel file will be placed in the `Downloads` folder of this application, but you may specify a different download folder when initializing the `ExtractDataPage` object. Details can be found in a later section.


When you are done, be sure to close the Webdriver so that it doesn't linger in your computer's running processes:

```
>>> page.driver.quit()
```

#### Downloading Multiple CLO Files ####

`main.py` contains a function that allows you to download the excel data for multiple CLO deals. To do so, first create a plain text file containing the names of the CLO deals that you wish to download, with each line containing a CLO deal like so:

![clo](./pictures/clo_deals.png?raw=true "clo")

Then, after having executed `python -i main.py`, call the function `download_multiple('path/to/text/file')`:

```
>>> download_multiple('test/names10.txt')
Thread 1:  80%|████████████████████████████████████████████████████████████▊               | 4/5 [06:15<01:35, 95.03s/it]
Thread 2:  60%|█████████████████████████████████████████████                              | 3/5 [05:04<03:27, 103.95s/it]
```

`download_multiple` by default creates two worker threads that will download the excel sheets for the CLO deals in the text file. The temp folders that the threads use are located in the `threading` folder. You can choose how many threads to spawn (max: 4) using the argument `num_threads`.

```
>>> download_multiple('test/names10.txt', num_threads=4)
Thread1:  50%|█████████████████████████████████████                                        | 1/2 [01:56<00:00, 58.50s/it]
Thread2: 100%|█████████████████████████████████████████████████████████████████████████████| 3/3 [02:32<00:00, 50.77s/it]
Thread3: 100%|█████████████████████████████████████████████████████████████████████████████| 3/3 [02:49<00:00, 56.62s/it]
Thread4:  50%|█████████████████████████████████████                                        | 1/2 [02:45<00:00, 82.57s/it]
```
It is recommended to use only two threads when downloading data for all the categories (Test Results, Tranches, Distributions, Holdings, Purchase/sale). Using four threads in the scenario may actually end up slower than using two threads. However, if you are downloading data for only one category, say Holdings, then you may likely benefit from using four threads to download the files. To download the results of only one category, use the argument `results'

```
>>> download_multiple('test/names10.txt', results='Holdings')
```


#### Specifying Download Folder ####

If you want the downloaded files to go to another folder instead of `Downloads`, you may specify the `dl_folder` argument when initializing the `ExtractDataPage` object.

```
>>> page = ExtractDataPage(dl_folder='new/path/to/folder')
>>> page.download('1828 CLO')
```

When downloading multiple CLOs, you can also specify the `dl_folder` argument.

```
>>> download_multiple('test/names10.txt', dl_folder='new/path/to/folder')
```

#### Logging In #####

For the creditflux website, all login data is stored in browser cookies, meaning that if you login to the website and save your cookies, you can continue using the site in the future without having to login again, provided that you re-use the cookies from the previous session.

There is already a cookies file located in the application folder that the program will automatically use when accessing the site. However, if for any reason the file is deleted or the cookies expire, you will first have to re-login using the `login_url` argument when initializing the `ExtractDataPage` object.

```
>>> page = ExtractDataPage(login_url='https://cloi.creditflux.com/Authentication/9c8e31917c8a89a3542aad76c730ba34')
Connecting to https://cloi.creditflux.com/ExtractData...
Logging in with url: https://cloi.creditflux.com/Authentication/9c8e31917c8a89a3542aad76c730ba34
Identifying filter elements...
>>>
```

Logging in using the example above will also create a new `cookies.pickle` file, which contains all the cookies needed to preserve the session for future access. 

#### Windows Chromedriver #####

On Windows, you must specify the path to the chromedriver when initializing the `ExtractDataPage` object.

```
>>> page = ExtractDataPage(chromedriver_path='path/to/chromedriver')
```

There is a copy of chromedriver located in the `chromedrivers/windows` folder, so you can type:
```
>>> page = ExtractDataPage(chromedriver_path='chromedrivers/windows/chromedriver.exe')
```


## ExtractDataPage ##

![](./pictures/extract_data_page_annotated.png?raw=true "annotated")
