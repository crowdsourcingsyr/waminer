import sys
import urllib
import lxml.html
from collections import deque
from urlparse import urlparse
import achecker
import model


TLD = ["com", "org", "net", "edu", "gov"]
MAX_QUEUE_NUM = 300


def crawl(url, urls):

    try:
        wa_issue = model.WebAccessibility(url=url)
        # Request document
        request = urllib.urlopen(url)

        # Start parsing received document
        page = lxml.html.fromstring(request.read())

        # Extract document metadata
        meta = page.xpath('//meta')
        for elem in meta:
            if elem.get('name') == "description":
                description = elem.get('content')
                print "Description: " + description
            if elem.get('name') == "keywords":
                keywords = elem.get('content')
                print "Keywords: " + keywords

        # Find all urls in document
        for link in page.xpath('//a/@href'):
            parse = urlparse(link)
            if "http://" in link:
                if parse.hostname is not None:
                    sep = parse.hostname.split(".")
                    if sep[-1] in TLD:
                        final = "http://www." + sep[1] + "." + sep[-1]
                        # print "http://www." + sep[1] + "." + sep[-1]
                        if final not in urls:
                            urls.append("http://www." + sep[1] + "." + sep[-1])

        # Find wa issues with document
        potential, likely, known, type_known, type_potential, type_likely = \
            data_extraction(url)

        # Save wa issues for this docuement
        wa_issue.known = known
        wa_issue.potential = potential
        wa_issue.likely = likely
        wa_issue.type_known = type_known
        wa_issue.type_potential = type_potential
        wa_issue.type_likely = type_likely
        wa_issue.description = description
        wa_issue.keywords = keywords

        wa_issue.save()

        # Continue crawl
        if urls:
            print "Number of urls in list: " + str(len(urls))
            if len(urls) < MAX_QUEUE_NUM:
                next_url = urls.popleft()
                print next_url
                crawl(next_url, urls)
    except:
        e = sys.exc_info()[0]
        print e
        if len(urls) > 0:
            cont_url = urls.popleft()
            crawl(cont_url, urls)


def data_extraction(url):
    wa_checker = achecker.Achecker()
    wa_checker.get_resource(url)
    potential = wa_checker.get_total_problems()
    likely = wa_checker.get_total_likely()
    known = wa_checker.get_total_errors()
    type_known, type_potential, type_likely = wa_checker.get_wa_type_ids()
    return potential, likely, known, type_known, type_potential, type_likely


def main():
    seed_url = 'https://www.whitehouse.gov/'
    # Create queue to hold urls
    urls = deque([])

    crawl(seed_url, urls)


if __name__ == "__main__":
    sys.exit(main())

