# -*- coding: utf-8 -*-
import glob
import os
import shutil
import time
import calendar
from datetime import date

import pickle
import pandas as pd
from retry import retry

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException



class ExtractDataPage:
    _EXCEL_MAX_ROWS = 5000
    _download_wait_time = 3

    _path_downloads_folder = None
    _path_temp_folder = None

    url = "https://cloi.creditflux.com/ExtractData"

    # Dropdowns
    _dropdown_xpaths = {
                                  'displayType':'//*[@id="displayType"]',
                                  'startMonth':'//*[@id="periodEndDateMonth1"]',
                                   'startYear':'//*[@id="periodEndDateYear1"]',
                                    'endMonth':'//*[@id="periodEndDateMonth2"]',
                                     'endYear':'//*[@id="periodEndDateYear2"]',
    } 

    # Filters
    _filter_xpaths = {
                                        'CLO':'//*[@id="dealId_chzn"]',
                                    'manager':'//*[@id="managerId_chzn"]',
                                   'arranger':'//*[@id="arrangerId_chzn"]',
                                    'trustee':'//*[@id="trusteeId_chzn"]',
                             'managerCounsel':'//*[@id="managerCounselId_chzn"]',
                            'arrangerCounsel':'//*[@id="arrangerCounselId_chzn"]',
                                    'CLOTags':'//*[@id="tagId_chzn"]'
    }

    _filter_selection_xpaths = {
                                        'CLO':'//*[@id="dealId_chzn"]/div/ul',
                                    'manager':'//*[@id="managerId_chzn"]/div/ul',
                                   'arranger':'//*[@id="arrangerId_chzn"]/div/ul',
                                    'trustee':'//*[@id="trusteeId_chzn"]/div/ul',
                             'managerCounsel':'//*[@id="managerCounselId_chzn"]/div/ul',
                            'arrangerCounsel':'//*[@id="arrangerCounselId_chzn"]/div/ul',
                                    'CLOTags':'//*[@id="tagId_chzn"]/div/ul'
    }

    # Download Button 
    _element_id_download_button = "excel"
    global_folder = r"C:\Users\znan3\OneDrive\Documents\creditflux_downloader"

    def __init__(self, 
                #dl_folder='./Downloads', 
                #temp_folder='./temp',
                #dl_folder=r'E:\大学文件\senior2\data crawling\creditflux_downloader\Downloads', 
                dl_folder = os.path.join(global_folder, 'Downloads'),
                #temp_folder=r'E:\大学文件\senior2\data crawling\creditflux_downloader\temp',
                temp_folder = os.path.join(global_folder, 'temp'),
                login_url=None, 
                headless=True, 
                verbose=True,
                chromedriver_path=None):
        self._verbose = verbose

        #file/folder paths must be converted to absolute paths for downloads to work on windows
        dl_folder = os.path.abspath(dl_folder)
        temp_folder = os.path.abspath(temp_folder)
        
        #print(dl_folder)

        if (chromedriver_path != None):
            chromedriver_path = os.path.abspath(chromedriver_path) 
        
        #######################################################################################

        self.driver = self._init_driver(dl_loc=temp_folder, headless=headless, chromedriver_path=chromedriver_path)

        self.enable_downloads(temp_folder)
        
        self._path_downloads_folder = dl_folder
        self._path_temp_folder = temp_folder

        self.connect()

        if login_url == None:
            self.load_session()
        else:
            self.login(login_url)

        self.driver.refresh()

        time.sleep(5)

        if self._verbose:
            print("Identifying filter elements...")

        #Selenium driver elements that represent the selection fields on the site
        self.display_type = Select(self.driver.find_element_by_xpath(self._dropdown_xpaths['displayType']))
        self.start_month = Select(self.driver.find_element_by_xpath(self._dropdown_xpaths['startMonth']))
        self.start_year = Select(self.driver.find_element_by_xpath(self._dropdown_xpaths['startYear']))
        self.end_month = Select(self.driver.find_element_by_xpath(self._dropdown_xpaths['endMonth']))
        self.end_year = Select(self.driver.find_element_by_xpath(self._dropdown_xpaths['endYear']))

        self.CLO_field = self.driver.find_element_by_xpath(self._filter_xpaths['CLO'])

        self.download_button = self.driver.find_element_by_id(self._element_id_download_button)
    
    #When the ExtractDataPage object is destroyed, the temp folder is cleared
    def __del__(self):
        self.clear_temp()

    #Function that must be called in order to allow downloads to work properly on Windows
    def enable_downloads(self, dirpath):
        dirpath = os.path.abspath(dirpath)
        self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dirpath}}
        self.driver.execute("send_command", params)
        
    def _init_driver(self, dl_loc, headless=True, chromedriver_path=None):
        options = webdriver.ChromeOptions()
        prefs = {   
                'download.default_directory':dl_loc,
                'download.directory_upgrade':True,
                'download.prompt_for_download':False,
                'safebrowsing_for_trusted_sources_enabled':False,
                'safebrowsing.enabled':False
                }
        if headless:
            options.add_argument("--headless")

        options.add_experimental_option("prefs", prefs)
        
        if chromedriver_path == None:
            return webdriver.Chrome(options=options)
        else:
            return webdriver.Chrome(executable_path=chromedriver_path, options=options)

    def output(self, message):
        if self._verbose:
            print(message)
    
    def login(self, login_url):
        if self._verbose:
            print("Logging in with url: %s" % login_url)

        self.driver.get(login_url) 
        self.driver.get(self.url)
        self.save_session()
    
    def connect(self):
        if self._verbose:
            print("Connecting to %s..." % self.url)

        self.driver.get(self.url) 

#    def save_session(self, filename="cookies.pickle"):
    def save_session(self, filename=os.path.join(global_folder, 'cookies.pickle')):
        if self._verbose:
            print("Saving cookies...")

        cookies = self.driver.get_cookies()

        for c in cookies:
            if 'expiry' in c.keys():
                c['expiry'] = int(c['expiry'])

        with open(filename, 'wb') as file:
            pickle.dump(cookies, file)
        
        file.close()

#    def load_session(self, filename="cookies.pickle"):
    def load_session(self, filename=os.path.join(global_folder, 'cookies.pickle')):
        if self._verbose:
            print("Loading cookies...")

        with open(filename, 'rb') as file:
            cookies = pickle.load(file)
        
        for c in cookies:
            self.driver.add_cookie(c)

    @retry((ElementClickInterceptedException, StaleElementReferenceException),
             tries=5, delay=1, jitter=1)
    def select_CLO(self, name):
        self.CLO_field.click()
        xpath = self._filter_selection_xpaths['CLO']
        selection = self.driver.find_element_by_xpath(xpath + '/li[contains(text(), "%s")]' % name)

        selection.click()


    def select_date_range(self, dateRange):
        self.start_month.select_by_value(dateRange[0])
        self.start_year.select_by_value(dateRange[1])
        self.end_month.select_by_value(dateRange[2])
        self.end_year.select_by_value(dateRange[3])

    def handle_selections(self, CLO, results, dateRange):
        if CLO != None:
            self.select_CLO(CLO)
        if results != None:
            self.display_type.select_by_visible_text(results)
        if dateRange != None:
            self.select_date_range(dateRange)

    def print_selected_CLOs(self):
        elements = self.driver.find_elements_by_class_name('search-choice')
        print([el.find_element_by_tag_name('span').text for el in elements])
    
    def clear_fields(self):
        self.clear_CLO_field()
        self.driver.find_element_by_xpath('//*[@id="main"]/form/div[1]/div/p[1]/label').click()

    def clear_CLO_field(self):
        elements = self.CLO_field.find_elements_by_class_name('search-choice-close')
        for button in elements:
            button.click()

    """
    Functions for downloading files from the page
    """

    def download(self, 
                CLO,
                results='all',
                startMonth='1',
                startYear='1999',
                endMonth=None,
                endYear=None,
                dest=None,
                _excelwriter=None,
                _closewriter=True):

        # Downloads the data for one CLO deal
        # Will automatically check if the first downloaded excel sheet reaches the
        # 5000 line limit that the creditflux website imposes. If so, then it is possible
        # that there is more data yet to be downloaded, and the code will try to find which 
        # date ranges to download from. All the downloaded data for the CLO will then be merged into 
        # one single excel sheet.

        if dest == None:
            dest = self._path_downloads_folder + '/%s.xlsx' % CLO
        
        if endMonth == None or endYear == None:
            current_date = date.today()
            endMonth = str(current_date.month)
            endYear = str(current_date.year)
        
        if _excelwriter == None:
            writer = pd.ExcelWriter(dest, engine='openpyxl', datetime_format='YYYY-MM-DD')
        else:
            writer = _excelwriter
        
        if results == "All" or results == "all":
            self._download_all_results(CLO, 
                                        startMonth,
                                        startYear,
                                        endMonth,
                                        endYear,
                                        dest,
                                        writer)
            return

        dateRange = [startMonth, startYear, endMonth, endYear]
        self.handle_selections(CLO, results, dateRange)

        if results.find('/') >= 0:
            results = results.replace('/', '_')
        
        self.download_button.click()

        filepath = self.newest(self._path_temp_folder)

        df = pd.read_excel(filepath, header=[1])

        if len(df) == self._EXCEL_MAX_ROWS:
            oldestDate, trimmed_df = self.trimmed(df)
            newDateRange = dateRange.copy()
            newDateRange[2] = str(oldestDate.month)
            newDateRange[3] = str(oldestDate.year)

            try:
                os.remove(filepath)
            except FileNotFoundError:
                pass

            self._redownload(dest, results, newDateRange, trimmed_df, writer, _closewriter)
        else:            
            df.to_excel(writer, sheet_name=results, index=False)
            writer.save()

            if _closewriter:
                writer.close()

            try:
                os.remove(filepath)
            except FileNotFoundError:
                pass

            self.clear_fields()

    def _redownload(self, dest, results, dateRange, old_df, _excelwriter, _closewriter):
        self.select_date_range(dateRange)
        self.download_button.click()

        filepath = self.newest(self._path_temp_folder)

        df = pd.read_excel(filepath, header=[1])

        merged_df = self.merged(old_df, df)

        if len(df) == self._EXCEL_MAX_ROWS:
            oldestDate, trimmed_df = self.trimmed(merged_df)
            newDateRange = dateRange.copy()
            newDateRange[2] = str(oldestDate.month)
            newDateRange[3] = str(oldestDate.year)

            try:
                os.remove(filepath)
            except FileNotFoundError:
                pass

            self._redownload(dest, results, newDateRange, trimmed_df, _excelwriter, _closewriter)
        else:
            merged_df.to_excel(_excelwriter, sheet_name=results, index=False)

            _excelwriter.save()

            if _closewriter:
                _excelwriter.close()

            try:
                os.remove(filepath)
            except FileNotFoundError:
                pass
            
            self.clear_fields()

    def _download_all_results(self,
                                CLO,
                                startMonth,
                                startYear,
                                endMonth,
                                endYear,
                                dest,
                                excelwriter):
            
            writer = excelwriter

            if self._verbose:
                print('Downloading Holdings...')

            self.download(CLO, results="Holdings", startMonth=startMonth,
                            startYear=startYear, endMonth=endMonth,
                            endYear=endYear, dest=dest, _excelwriter=writer,
                            _closewriter=True)
        
            
            appender = pd.ExcelWriter(dest, engine='openpyxl', datetime_format='YYYY-MM-DD', mode='a')

            if self._verbose:
                print("Downloading Test Results...")
            
            self.download(CLO, results="Test Results", startMonth=startMonth,
                            startYear=startYear, endMonth=endMonth,
                            endYear=endYear, dest=dest, _excelwriter=appender,
                            _closewriter=False)

            if self._verbose:
                print('Downloading Tranches...')
            
            self.download(CLO, results="Tranches", startMonth=startMonth,
                            startYear=startYear, endMonth=endMonth,
                            endYear=endYear, dest=dest, _excelwriter=appender,
                            _closewriter=False)

            if self._verbose:
                print('Downloading Distributions...')

            self.download(CLO, results="Distributions", startMonth=startMonth,
                            startYear=startYear, endMonth=endMonth,
                            endYear=endYear, dest=dest, _excelwriter=appender,
                            _closewriter=False)

            if self._verbose:
                print("Downloading Purchase/sale...")

            self.download(CLO, results="Purchase/sale", startMonth=startMonth,
                            startYear=startYear, endMonth=endMonth,
                            endYear=endYear, dest=dest, _excelwriter=appender,
                            _closewriter=False)


    @retry((ValueError, FileNotFoundError), tries=10, delay=1)
    def newest(self, folder):
        list = glob.glob(folder + '/*')
        filepath = max(list, key=os.path.getctime)
        while filepath.find('.crdownload') >= 0:
            time.sleep(1)
            list = glob.glob(folder + '/*')
            filepath = max(list, key=os.path.getctime)

        return filepath
        
    def merged(self, df1, df2, dateColumn='As Of'):
        return pd.concat([df1,df2], ignore_index=True)

    def trimmed(self, df, dateColumn='As Of'):
        N = len(df[dateColumn])
        oldestDate = df[dateColumn][N-1]
        
        return oldestDate, df[df[dateColumn] != oldestDate]
    
    def clear_temp(self):
        list = glob.glob(self._path_temp_folder + '/*')
        for filepath in list:
            try:
                os.remove(filepath)
            except FileNotFoundError:
                pass



    




