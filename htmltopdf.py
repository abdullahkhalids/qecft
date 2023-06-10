#!/usr/bin/env python3

from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

index_html = Path("build" , "index.html")
keep_going = True

# this page break is only interpreted when printing as PDF
page_break = BeautifulSoup('<p style="page-break-before: always">', "lxml")

# concatenated pages
concatenated_pages = []
curr_section = ""

with open(index_html) as f:
    content = f.read()
    index_soup = BeautifulSoup(content, "lxml")
    toc = index_soup.find("div", id="sidebar-primary")
    title = index_soup.find("h1", id="brand-title")
    concatenated_pages.append(title)
    # delete search box
    index_soup.find("form", id="search-box").decompose()
    # Add a pagebreak after the title and the TOC
    # Add a placeholder image. The author's favicon will do.
    # Even if it doesn't render, it counts as a dummy image
    concatenated_pages.append(BeautifulSoup('<img src="build/images/Cover.png">', "lxml"))
    concatenated_pages.append(page_break)
    # Optional: TOC links need to be redirected to those in the book
    # add TOC
    concatenated_pages.extend(toc)

while keep_going:
    with open(index_html) as f:
        content = f.read()
        soup = BeautifulSoup(content, "lxml")
        # find the next link if it's there
        next_link = soup.find("a", id="next-link")
        # select article's content
        content_article = soup.find("div", id="main-container")
        if next_link:
            next_link_url = next_link["href"]
            next_link_parts = next_link_url.split("/")
            next_section = next_link_parts[-2]
            if curr_section != next_section:
                curr_section = next_section
                # insert a page break after each section
                concatenated_pages.append(page_break)
            next_page = next_link_parts[-1]
            print("{}/{}".format(next_section, next_page))
            index_html = Path("build", next_section, next_page, "index.html")
        else:
            keep_going = False
            print("Reached last page")

        # replace the hr at the end of the page
        hr = content_article.find_all("hr")[-1]
        hr.decompose()
        # append page contents
        concatenated_pages.extend(content_article)

# convert concatenated pages as string and reparse it
# although inefficient, it's plenty fast already
new_html = ''.join(str(s) for s in concatenated_pages)
new_soup = BeautifulSoup(new_html, "lxml")

# load the jinja template
# need to set comment characters to something else to avoid mathjax clashes
with open("website-jinja-template/base.html") as f:
    template = Template(f.read(), comment_start_string="abcde", comment_end_string="abcde")

# substitute the template with the build directory
base = template.render(SITEURL = "build")
base_soup = BeautifulSoup(base, "lxml")
# replace body with the concatenated pages
base_body = base_soup.find("div", id="body-container")
base_body.replace_with(new_soup)

# delete the header/footers, we don't need them anymore
for header in base_soup.find_all("div", id="content-header"):
    header.decompose()
for footer in base_soup.find_all("div", id="content-footer"):
    footer.decompose()
# replace cell-outputs containing svgs with just the svgs
# TODO: resize inline SVG to fit on page (specifically parent container width)
for img in base_soup.find_all("div", class_="cell-output"):
    svg = img.find("svg")
    if svg:
        img.replace_with(svg)

# Adjust links for relative file paths
for has_href in base_soup.find_all(href=True):
    has_href["href"] = has_href["href"].replace("https://abdullahkhalid.com/qecft/", "build/")
for script in base_soup.find_all("script",  src=True):
    script["src"] = script["src"].replace("https://abdullahkhalid.com/qecft/", "")
for img in base_soup.find_all("img",  src=True): #, id="src"):
    img["src"] = img["src"].replace("../../", "")

# insert additional CSS at the end of the head
# test_css = BeautifulSoup().new_tag("link", rel="stylesheet", href="https://abdullahkhalid.com/qecft/static/css/codemirror.min.css", type_="text/css")
# base_soup.head.append(test_css)

# Save HTML to a file
with open("book.html", "w") as f:
    f.write(str(base_soup))
    print("Wrote book.html")

# Use chromium headless to print HTML to PDF
def run(playwright):
    chromium = playwright.chromium
    # Flags added for hardware acceleration
    # TODO: renders links different colors if they are visited
    browser = chromium.launch(headless=True, args=["--incognito", "--use-gl=egl", "--ignore-gpu-blocklist"])
    context = browser.new_context()
    page = context.new_page()
    html = Path("book.html").absolute().as_uri()
    start = time.time()
    # open the page and wait for it to finish
    page.goto(html, wait_until="load")
    end = time.time()
    print("Took {} seconds to load page".format(end-start))
    print("Waiting to load Mathjax")
    time.sleep(10)
    print("Printing PDF now")
    start = time.time()
    page.pdf(path="book.pdf",
             display_header_footer=True,
             # margins are required for the header/footer templates
             header_template=' ',
             # style footer location
             footer_template='<span class="pageNumber" style="position: absolute; left: 62%; font-size: 10px;"></span>',
             margin={
                 "top": "1cm",
                 "right": "2cm",
                 "bottom": "1cm",
                 "left": "2cm",
             })
    end = time.time()
    print("Took {} seconds to print pdf".format(end - start))
    browser.close()

with sync_playwright() as playwright:
    print("Running playwright, please wait...")
    run(playwright)
    print("PDF saved to book.pdf")
