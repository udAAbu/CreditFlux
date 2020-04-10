# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 22:06:27 2020

@author: znan3
"""


# -*- coding: utf-8 -*-

import glob
import time
import threading
import traceback
import os
from argparse import ArgumentParser

from tqdm import tqdm

from creditflux import ExtractDataPage



path_downloads_folder = "./Downloads"
path_chromedrivers_folder = "./chromedrivers/windows/chromedriver.exe"
path_logs_folder = "./logs"
path_temp_folder = "./temp"

#need to be changed
global_folder = r"C:\Users\znan3\OneDrive\Documents\creditflux_downloader"

path_thread_temp_folder = ["threading/thread%d" % i for i in range(1,5)]

def clear_logs():
    list = glob.glob(path_logs_folder + '/*')
    for filepath in list:
        with open(filepath, 'w') as f:
            f.write('')

def func(names, args):
    page = ExtractDataPage(dl_folder=args['dl_folder'], temp_folder=args['temp_folder'], verbose=False, chromedriver_path=args['chromedriver_path'])

    for deal_name in tqdm(names, desc=args['thread_name']):
        try:   
            path = os.path.join(global_folder, 'Downloads\%s.xlsx') % deal_name
            print(path)
            page.download(deal_name, results=args['results'], dest=path)
        except:
            with open(os.path.join(global_folder, 'logs\errors'), 'a') as f:
                f.write(traceback.format_exc())
            
            with open(os.path.join(global_folder, 'logs\failed'), 'a') as f:   
                f.write(deal_name + '\n')
            
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        finally:
            page.clear_temp()


    page.driver.quit()
                


def download_multiple(file, 
                    results='all',
                    num_threads=2,
                    dl_folder = os.path.join(global_folder, 'Downloads'),
                    chromedriver_path = os.path.join(global_folder, 'chromedrivers\windows\chromedriver.exe'),
                    abs_path=None
                    ):
    if num_threads > 4:
        print("Error: Thread count may not exceed 4")

    if abs_path == None:
        abs_path = ""
    else:
        abs_path = abs_path + '/'


    startTime = time.time()

    with open(file, 'r') as f:
        names = [l.rstrip('\n') for l in f]
    
    subset = []
    for i in range(num_threads):
        subset.append([])

    for i in range(len(names)):
        subset[i % num_threads].append(names[i])
    

    threads = []
    for i in range(num_threads):

        args = {}
        args['results'] = results
        args['num_threads'] = num_threads
        args['thread_name'] = "Thread%d" % (i+1)
        args['temp_folder'] = os.path.abspath(abs_path + path_thread_temp_folder[i])
        args['dl_folder'] = dl_folder
        args['chromedriver_path'] = chromedriver_path

        t = threading.Thread(target=func, args=(subset[i], args,))
        threads.append(t)
    
    for t in threads:
        t.start()

    for t in threads:
        t.join()


    endTime = time.time()
    runTime = endTime - startTime

    print("Completed in %d seconds" % runTime)

def clear_folder(folder):
    pass

def download_single(dealname):
    page = ExtractDataPage(chromedriver_path=os.path.join(global_folder, 'chromedrivers\windows\chromedriver.exe'))
    print('downloading all the results of ', dealname)
    page.download(dealname)
#    print('done')

import sys

if __name__ == '__main__':
    if(sys.argv[1].lower()=='yes'):
        deal_name = sys.argv[2]
        download_single(deal_name)
        print("done")
    elif(sys.argv[1].lower()=='no'):
        filepath = sys.argv[2]
        download_multiple(filepath)
        print('done')
    else:
        print('not a valid request') 
    