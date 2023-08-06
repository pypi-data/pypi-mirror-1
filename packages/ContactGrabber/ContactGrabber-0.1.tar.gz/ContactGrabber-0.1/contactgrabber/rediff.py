from base import SimpleCurl, EMAIL_PATTERN, uniqify

LoginUrl = "https://mail.rediff.com/cgi-bin/login.cgi?"

def grab_rediff(username, password):

    mycurl = SimpleCurl()

    page = mycurl.get_page(LoginUrl +
                           "login=%s&passwd=%s&submit=GO&FormName=existing" %
                            (username, password))

    page_parts = page.split("session_id=")
    if len(page_parts) < 2: # login unsuccessful
        return []
    session_id = page_parts[1].split("&")[0]

    emails = []
    address_url = '/bn/address.cgi?login=%s&session_id=%s' % (username, session_id)
    while True:
        page = mycurl.get_page('http://f1mail.rediff.com' + address_url)
        emails.extend(EMAIL_PATTERN.findall(page))

        next_url_last = page.find('">Next<')
        if next_url_last == -1:
            break
        next_url_first = page.rfind('<a HREF="', 0, next_url_last) + 9
        address_url = page[next_url_first:next_url_last]

    return uniqify(emails)
