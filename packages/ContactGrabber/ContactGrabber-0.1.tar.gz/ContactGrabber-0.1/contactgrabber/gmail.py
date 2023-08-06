from base import SimpleCurl, EMAIL_PATTERN

LoginUrl = "https://www.google.com/accounts/ServiceLoginAuth?service=mail"
ExportUrl = "https://mail.google.com/mail/contacts/data/export?exportType=ALL&groupToExport=&out=GMAIL_CSV"

def grab_gmail(username, password):

    login_values = str("&ltmpl=default&ltmplcache=2&service=mail&rm=false&hl=en&Email=%s&Passwd=%s&PersistentCookie=true&rmShown=1&null=Sign%%20In"
                       % (username, password))

    mycurl = SimpleCurl()
    mycurl.get_page(LoginUrl + login_values)
    page = mycurl.get_page(ExportUrl)
    return EMAIL_PATTERN.findall(page)
