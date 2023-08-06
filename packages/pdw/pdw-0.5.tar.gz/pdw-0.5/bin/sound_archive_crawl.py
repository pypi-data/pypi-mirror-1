#!/usr/bin/env python
# Crawl British Library Sound Archive web catalogue and download work details 
import os
import time
import re
from mechanize import Browser

# starting search page
SEARCH_PAGE_URL = 'http://cadensa.bl.uk/cgi-bin/webcat'
# do not change from 1900 at present
YEAR = 1900
# path to directory where we will save spidered pages
# pages will be saves in this directory with name <year>_<item_no>.html
import pdw
PAGE_CACHE = pdw.conf().get('DEFAULT', 'cache_dir')
debug = False
verbose = True
def _print(msg, error=False):
    if verbose or error:
        print(msg)

def main():
    br = Browser()
    br.addheaders = [ ('User-agent', 'Firefox') ]
    br.set_handle_robots(False)
    _print('Opening url: %s' % SEARCH_PAGE_URL)
    br.open(SEARCH_PAGE_URL)

    # follow second link with element text matching regular expression
    _print('Going to Advanced search page')
    br.follow_link(text = 'Advanced search')
    assert br.viewing_html()

    br.select_form(name='searchform')
    _print('Getting results for year %s' % YEAR)
    br['pubyear'] = str(YEAR)
    br.submit() 
   
    # base is the index of first result item on each page of results
    # this is hardcoded for 1900 at present
    for base in (1,21,41,61,81,101,121):
        _print('Looping through results on page %s' % base)
        if base > 1: # jump to page of results
            br.select_form('hitlist')
            # form_type is hidden usually so have to disable readonly
            # see http://wwwsearch.sourceforge.net/ClientForm/
            jumpPage = 'JUMP^%s' % base  
            _print('Jumping to page: %s' % jumpPage)
            control = br.find_control('form_type')
            control.readonly = False
            control.value = jumpPage
            # br['form_type'] = jumpPage
            # NB: submit is *not* the same as click: submit = open(click())
            # if we just use submit() then mechanize will click on first input
            # control on page which happens to be image saying Next which 
            # takes you to next set of results. Consequence of this is that:
            # a) always go to first set of extra results (21)
            # b) after details of first result are extracted will fail on
            # second because it does a back and reload which is resubmitting
            # this first page in which Next has been clicked
            # e.g. 21-40 list page -> details result 21 -> back -> reload
            # (next) -> 41-61 list page -> look for result 22 -> exception
            #
            # Solve this by delving into internals of ClientForm class whence
            # we see that in order to submit a form w/o clicking on a button
            # must use _switch_click
            br.open(br._switch_click("request"))
            _print('List page is %s' % br.geturl())
        for ii in range(20):
            ii += base
            if debug:
                ff = open('./pages/basepage%s.html' % ii, 'w')
                ff.write(br.response().read())
                ff.close()
            
            br.select_form('hitlist')
            buttonName = 'VIEW^%s' % ii
            _print(buttonName)
            # must use submit and not click
            br.submit(buttonName)
            currentUrl = br.geturl()
            _print('Saving item: %s (url is %s)' % (ii, currentUrl))
            savePath = os.path.join(PAGE_CACHE, '%s_%s.html' % (YEAR, ii))
            ff = open(savePath, 'w')
            ff.write(br.response().read())
            ff.close()

            time.sleep(1)  # give server a break
            br.back()
            # have to reload or we get an error ...
            br.reload()

if __name__ == '__main__':
    main()
