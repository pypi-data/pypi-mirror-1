from base import SimpleCurl, EMAIL_PATTERN, uniqify

LoginUrl = "https://login.yahoo.com/config/login?"
ExportUrl = "http://address.yahoo.com/yab/us/Yahoo_ab.csv"

def grab_yahoo(username, password):

    mycurl = SimpleCurl()
    mycurl.get_page(LoginUrl + "login=%s&passwd=%s" % (username, password))
    page = mycurl.get_page(ExportUrl)
    return uniqify(EMAIL_PATTERN.findall(page))
