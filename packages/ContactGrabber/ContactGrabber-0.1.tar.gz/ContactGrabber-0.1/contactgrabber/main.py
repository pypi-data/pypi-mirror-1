from rediff import grab_rediff
from gmail import grab_gmail
from yahoo import grab_yahoo

def grab_contacts(username, password, site):
    """
    Grabs contacts from GMail, Yahoo!, Rediff etc.
    How to use:

    from contactgrabber import grab_contacts
    try:
        emails = grab_contacts('mike', 'password_of_mike', 'rediff')
        if len(emails) == 0:
            print 'No contacts found. Did you enter invalid user ID / pasword?'
        print str(emails)
    except:
        print 'Invalid UserID/Password'

    Currently supported sitenames: 'rediff', 'gmail', 'yahoo'
    """

    if site == 'rediff':
        return grab_rediff(username, password)
    if site == 'gmail':
        return grab_gmail(username, password)
    if site == 'yahoo':
        return grab_yahoo(username, password)
    raise Exception(site + ' is not supported yet. You can contribute to the project at http://code.google.com/p/pycontactgrabber/')
