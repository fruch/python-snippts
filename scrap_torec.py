from selenium import selenium

def main():

    sel = selenium("localhost", \
            4444, "*firefox", "http://www.torec.net/")
    sel.start()
    sel.open("http://www.torec.net/")
    sel.type("search", 'House S07E03')
    sel.submit('srchForm')
    sel.wait_for_page_to_load(15000)
    sel.click("//*[contains(@href,'sub_id')]")
    sel.wait_for_page_to_load(30000)
    sel.select('download_version', '*LOL*')
    
    print sel.get_text("//*[@id='download_version']/option[1]")
    print sel.get_text("//*[@id='download_version']/option[2]")
    
    sel.click("//*[@id='download_version_btn']")

    '''
    import urllib
    import urllib2
    params = urllib.urlencode(dict(sub_id='24802', code='8FCA9EA3B4919784B7BBC2C29CADB3B0', guest='', timewaited=-1))
    url = "http://www.torec.net/ajax/sub/download.asp"
    headers = { 'HTTP_X_REQUESTED_WITH' : 'XMLHttpRequest' }
    req = urllib2.Request(url, params, headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print the_page
    '''
    
if __name__ == "__main__":
    main()