#!/usr/bin/env python

# HTML text to DOM library
from lxml import html

# Net and url based tools
import urllib2, urllib
from urlparse import urlparse, urlunparse

# To cleanup our book titles so that they can be used as filenames
from re import compile

# Tools for working with files and directories
from os import makedirs, path, getcwd

# Module that allows us to prompt for a password without echoing
from getpass import getpass

# Standard logging module
import logging

# A regex for selecting out the characters that are invalid and replacing them.
# TODO Checkout putting Unicode equivalent characters instead...
INVALID_FILE_CHARS = compile(r'[?%*:|"<>/]')

# A mapping between logging strings and logging levels.
LOGLEVELS = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL}

# The default logging level for this program
DEFAULT_LOGGING = 'info'

# The list of input values necessary to request pdf generation
SAFARI_REQUESTPDF_FORM = {'__className': 'pdfdownload',
                          '__dlid': '',
                          '__pdfcurrentxmlid': '',
                          '__callOmniture': '1',
                          '__version': '1.1.1',
                          '__pdfaction': 'regenerate'}

URL_SAFARI_LOGIN = 'http://my.safaribooksonline.com/login'
URL_SAFARI_DOWNLOADS = 'http://safari.oreilly.com/mydownloads'
URL_SAFARI_REQUESTPDF = 'http://safari.oreilly.com/_ajax_overlaypdf' 

def config_cookie_support():
    """Monkey patch the standard library modules to keep session cookies."""
    # If you need to handle cookies in python, you have to monkey patch the
    # libraries used to fetch files.  The most common libraries used for this
    # purpose are urllib and urllib2 (thankfully, they're consolidated in
    # Python 3, but we're not there yet...)
    logging.error('Monkey patching system libraries with cookie support.')

    # If you are having problems with your cookies, it will be useful to setup
    # an LWP Cookie jar, which allows us to inspect cookies in a human readable
    # format. Use the following code instead.
    #
    # from cookielib import LWPCookieJar
    # global cj
    # cj = LWPCookieJar()
    #
    # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    import urllib2
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    # We depend on urllib2 to perform our patching, so we know it's here
    urllib2.install_opener(opener)

    from sys import modules

    # If the program has urllib loaded, we'll patch that, as well.
    if 'urllib' in modules:
        logging.debug('urllib loaded, monkey patching it for cookie support')
        modules['urllib']._urlopener = opener

    # Ideally, we'd also like to patch lxml so that we can use it's built in
    # facilities with cookies, as well, but lxml sometimes uses urllib and
    # sometimes uses libxml's web facilities, which we can't patch.  You have
    # to be aware of this and work around the limitations.

def safari_login(user, password):
    """Login to the Safari website to load a session cookie."""
    logging.debug("Connecting to the Safari website at %s." % URL_SAFARI_LOGIN)
    doc = html.fromstring(urllib2.urlopen(URL_SAFARI_LOGIN).read(), base_url=URL_SAFARI_LOGIN)


    login_forms = doc.cssselect('form[name="login"]')
    if not login_forms:
        logging.critical('Unable to find the login form, can\'t continue.')
        raise EOFError

    login_form = login_forms[0]
    login_form.fields['login'] = user
    login_form.fields['password'] = password

    # For the purpose of this script, we assume success, so we don't care about
    # the result.  We really should verify this, though.
    logging.info("Logging into the account")
    logging.debug('Submitting login form')

    # lxml uses urllib by default for downloads.  Since we've patched it for
    # cookie support, this is sufficient for our needs.
    html.submit_form(login_form)

def safari_get_downloads(filename=None,syncpath=getcwd()):
    """Connect to Safari to retrieve the data, and then download any files not
    on the local disk.  Request any unavailable PDFs if necessary."""
    # Read and parse downloads
    logging.info("Retrieving Safari downloads page from %s" % filename)
    doc = html.fromstring(urllib.urlopen(filename).read(), base_url=URL_SAFARI_DOWNLOADS)

    # Get the list of table headers
    headers = [header.text_content().strip().lower() for header in doc.cssselect("table.Content th")]

    # In order to be a bit more resilient to changes in the document, we'll try
    # to find the information we care about in the table.
    metadata = ['book', 'section', 'pdf']
    columns = {}
    for column in metadata:
        for header in enumerate(headers):
            if column in header[1]:
                # We store a one based index for css selection
                columns[column] = header[0] + 1

    if len(metadata) != len(columns):
        logging.critical("Unable to find download metadata for these categories: '%s' from headers:\n%s" % \
          ("','".join(metadata), "".join([html.tostring(el) for el in headers])))
        raise EOFError


    ###################################################
    # Some helper functions for extracting cell content
    ###################################################
    def get_link(cell):
        "Get the href of the first a node, or return an empty string"
        link = cell.cssselect('a') and cell.cssselect('a')[0].attrib['href'] or ''
        # This dance cleans up some technically valid, but useless links like '#'
        link = urlunparse(urlparse(link))
        return link

    def get_text(cell):
        "Return the text content of the cell, strip leading and trailing whitespace."
        text = cell.text_content().strip()

        # Because of a bug either in lxml, or the libraries it depends on
        # (libxml, libxslt), it reads the utf-8 document and treats it as
        # if it were latin-1.  We fix the the encoding mistake.
        try:
            return text.encode('latin-1').decode('utf-8')
        except UnicodeEncodeError:
            # This probably means that the text was properly decoded and it
            # contains characters not valid in the latin-l set.  We'll let this
            # pass.
            return text
        except UnicodeDecodeError:
            # Just in case this bug exists only on my system, we'll ignore it
            # if the 'fix' doesn't work.
            return text

    # We'll keep track of whether or not we requested pdfs so that we can print
    # a helpful error message
    requested_pdfs = False

    # Extract a list or table row elements, each one containing data about one
    # download
    rows = doc.cssselect("table.Content tbody tr")
    for index, row in enumerate(rows):
        try:
            titlecell = row.cssselect('td:nth-child(%d)' % columns['book'])[0]
            sectioncell = row.cssselect('td:nth-child(%d)' % columns['section'])[0]
            downloadcell = row.cssselect('td:nth-child(%d)' % columns['pdf'])[0]
        except IndexError:
            logging.error("Unable to extract download data from cell:\n%s" % html.tostring(row))
            continue

        # Safari book downloads don't have a section text.
        if get_text(sectioncell):
            progress_message = "Handling Section '%s' of Book '%s'" % (get_text(sectioncell), get_text(titlecell))
            pdffile = '%s.pdf' % get_sanitized_path([syncpath, get_text(titlecell), get_text(sectioncell)])
            requestid = get_link(sectioncell).lstrip('/')
        else:
            progress_message = "Handling Book %s" % get_text(titlecell)
            pdffile = '%s.pdf' % get_sanitized_path([syncpath, get_text(titlecell), get_text(titlecell)])
            requestid = get_link(titlecell).lstrip('/')

        if not path.exists(pdffile):
            logging.info("%d of %d:%s" % (index+1, len(rows), progress_message))
            if get_link(downloadcell):
                logging.debug("Downloading file from %s" % get_link(downloadcell))
                downloadfile(get_link(downloadcell), pdffile)
            else:
                logging.debug("Reqeusting PDF generation for ID %s" % requestid)
                requestpdf(requestid, requestid)
                requested_pdfs = True
        else:
            logging.debug("%d of %d:%s" % (index+1, len(rows), progress_message))

    if requested_pdfs:
        logging.info("Not all of the missing PDFs were found.  They have been " \
        "requested from Safari, so please rerun this after generation is " \
        "complete.")

def downloadfile(link,filepath):
    """Download the file from the given link, and save it to the specified filepath"""
    filedir = path.dirname(filepath)
    try:
        makedirs(filedir)
    except OSError:
        # The error is raised even if the directory already exists.  If so, we
        # ignore the error.
        if not path.exists(filedir):
            logging.error('Unable to create directory: %s' % filedir)
            return

    # urllib.urlretrieve
    urllib.urlretrieve(link, filepath)
    #response = urllib2.urlopen(link)
    #with open(filepath, 'w') as pdf:
    #    pdf.write(response.read())

def get_sanitized_path(pathlist):
    """Turn a list of path elements into a path, while sanitizing the characters"""
    return path.join(*[INVALID_FILE_CHARS.sub('_', subpath) for subpath in pathlist])

def requestpdf(downloadid, xmlid):
    """Submit a PDF generation request.  This is now an AJAX only interface, so
    we hack it instead of connecting to a web page to fill out the form."""
    form_values = SAFARI_REQUESTPDF_FORM.copy()
    form_values['__dlid'] = downloadid
    form_values['__pdfcurrentxmlid'] = xmlid

    postdata = urllib.urlencode(form_values)

    response = urllib2.urlopen("%s?%s" % (URL_SAFARI_REQUESTPDF, postdata))
    response.read()

def prompt_user_pass(user, password):
    "Request a user and password, taking into account data from the command line."
    if not user:
        user = raw_input("Please input the username for your Safari account.\n")
    if not password:
        password = getpass("Please input the password for your Safari account.\n")
    return user, password

def main():
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option('-u','--username',
                      dest='username',
                      default=None,
                      help='Username of the Safari account to sync')
    parser.add_option('-p','--password',
                      dest='password',
                      default=None,
                      help='Password of the Safari account to sync')
    parser.add_option('-d','--dest',
                      dest='path',
                      default='books',
                      help='Path of the folder to sync downloads to.  This defaults to books subdirectory.')
    parser.add_option('-l','--logging',
                      dest='loglevel',
                      default=DEFAULT_LOGGING,
                      help='Change the logging level of this application.  Possible choices are "%s".' % ', '.join(LOGLEVELS.keys()))
    # This normally won't be used unless someone is debugging the html
    # scraping.  In that case, it saves the effort of supplying the user and
    # password and connecting to the server.
    parser.add_option('-s','--simulate',
                      dest='simulate',
                      default=None,
                      help='Provide a local copy of the downloads page for simulation.')

    options, arguments = parser.parse_args()

    # We only allow a set list of log levels.  If the one supplied is bogus,
    # use the default, but notify the users in case that means we've munged
    # some other parameter.
    if options.loglevel not in LOGLEVELS:
        logging.error("Invalid log level '%s', defaulting to '%s'" % (options.loglevel, DEFAULT_LOGGING))
        logging.basicConfig(level=LOGLEVELS[DEFAULT_LOGGING], format="%(levelname)-8s %(message)s")
    else:
        logging.basicConfig(level=LOGLEVELS[options.loglevel], format="%(levelname)-8s %(message)s")

    if options.simulate:
        filename = path.realpath(path.join(getcwd(), options.simulate))
    else:
        filename = URL_SAFARI_DOWNLOADS

        if not options.username or not options.password:
            options.username, options.password = prompt_user_pass(options.username, options.password)

        # Set up urllib2 to keep cookies.
        config_cookie_support()
        safari_login(options.username,options.password)

    safari_get_downloads(filename, options.path)

if __name__ == "__main__":
    main()
