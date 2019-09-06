from pprint import pprint
bookstore_url = 'https://northwestern.bncollege.com/shop/northwestern/page/find-textbooks'
all_books = []

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import sys
import time
from random import randint

# bookstore_url = "http://carleton.bncollege.com/webapp/wcs/stores/servlet/TBWizardView?catalogId=10001&langId=-1&storeId=87738"



browser = None

def new_browser():
  global browser
  if browser:
    browser.quit()
  opts = webdriver.chrome.options.Options()
  # switch numbers in this around to get past rate limiting
  opts.add_argument("user-agent=Mozilla/{}.{} (Macintosh; Intel Mac OS X 10.{}; rv:{}.0) Gecko/20100101 Firefox/57.0".format(randint(1,9), randint(1,9), randint(1,15), randint(40,60)))
  browser = webdriver.Chrome(chrome_options=opts,executable_path='C:/Users/changd/Downloads/chromedriver_win32/chromedriver.exe')

  time.sleep(3)

new_browser()

def click_on(dropdown_item):
  browser.execute_script("arguments[0].scrollIntoView(false);", dropdown_item)
  while True:
    try:
      dropdown_item.click()
      return
    except WebDriverException:
      time.sleep(0.2)

def get_classes():
  def get_dropdown_values(inputs, path):
    time.sleep(0.3)
    click_on(inputs[0])
    dropdown_data = {}
    for i in range(len(inputs[0].find_element_by_xpath('..').find_elements_by_class_name('result'))):
      # if scraping fails halfway through, you can uncomment this to skip the first i subjects
      # if i < 37 and len(inputs) == 3:
      #   continue
      inputs[0].clear()
      click_on(inputs[0])
      res = inputs[0].find_element_by_xpath('..').find_elements_by_class_name('result')[i]
      res_text = res.text.strip()
      if len(res_text) > 0:
        if len(inputs) > 1:
          click_on(res)
          dropdown_data[res_text] = get_dropdown_values(inputs[1:], path + [res_text])
        else:
          print("\t".join(path + [res_text]))
          dropdown_data[res_text] = []

    return dropdown_data

  browser.get(bookstore_url)
  while len(browser.find_elements_by_class_name('bookRowContainer')) == 0:
    time.sleep(0.3)

  inputs = browser.find_element_by_class_name('bookRowContainer').find_elements_by_class_name('bncbTextInput')
  return get_dropdown_values(inputs, [])

def get_books_for_class(lookup_path):
  if randint(0,4) == 0:
    new_browser()
  browser.get(bookstore_url)
  while len(browser.find_elements_by_class_name('bookRowContainer')) == 0:
    time.sleep(1)
  inputs = browser.find_element_by_class_name('bookRowContainer').find_elements_by_class_name('bncbTextInput')
  for i in range(len(lookup_path)):
    click_on(inputs[i])
    for res in inputs[i].find_element_by_xpath('..').find_elements_by_class_name('result'):
      if res.text.strip() == lookup_path[i]:
        click_on(res)
        break
    time.sleep(0.5)

  click_on(browser.find_element_by_id('findMaterialButton'))
  if len(browser.find_elements_by_css_selector('.findMaterialsButton.largeDisableBtn')) > 0:
    print("^".join(lookup_path + ['none']*4))
    return

  while len(browser.find_elements_by_class_name('courseOverView_panel')) == 0:
    time.sleep(1)

  if len(browser.find_elements_by_class_name('noMaterial_assigned')) > 0:
    print("^".join(lookup_path + ['none']*4))
    return

  books = []
  for book_el in browser.find_elements_by_class_name('book-list'):
    book_data = {}
    book_data["title"] = book_el.find_element_by_css_selector('h1 a').text

    try:
        book_data["author"] = book_el.find_element_by_css_selector('h2 i').text
    except:
        book_data["author"] = ""
        continue

    book_data["edition"] = ""
    book_data["isbn"] = ""
    for strong in book_el.find_elements_by_css_selector('strong'):
      if "isbn" in strong.text.lower():
        book_data["isbn"] = strong.find_element_by_xpath('..').text
      elif "edition" in strong.text.lower():
        book_data["edition"] = strong.find_element_by_xpath('..').text
    books.append(book_data)
    print("^".join(lookup_path + list(book_data.values())))
    all_books.append(book_data)
  return books

def get_all_books(data, path=[]):
  for k in data:
    path2 = path + [k]
    if isinstance(data[k], list):
      data[k] = get_books_for_class(path2)
    else:
      get_all_books(data[k], path2)

# uncomment this to get a print-out of all classes
# get_classes()



# uncomment this to get actual class book data
# put output from above command into string to get it out

classes = """
CHEM    110-0   ALL
CHEM    151-0   ALL
CHEM    161-0   ALL
CHEM    171-0   ALL
CHEM    181-0   ALL
CHEM    210-1   ALL
CHEM    212-1   ALL
CHEM    232-1   ALL
CIV_ENV 216-0   ALL
COMP_ENG        203-0   ALL
COMP_SCI        111-0   ALL
COMP_SCI        211-0   ALL
COMP_SCI        214-0   ALL
DSGN    106-1   ALL
ECON    201-0   20
ECON    201-0   40
ECON    202-0   20
ECON    281-0   ALL
ECON    310-1   ALL
ECON    310-2   ALL
ECON    311-0   ALL
ELEC_ENG        202-0   ALL
ES_APPM 252-1   ALL
GEN_ENG 205-1   ALL
GEN_ENG 205-3   ALL
MATH    214-0   ALL
MATH    218-1   ALL
MATH    220-1   ALL
MATH    220-2   ALL
MATH    226-0   ALL
MATH    228-1   ALL
MATH    228-2   ALL
MATH    230-1   ALL
MATH    234-0   ALL
MAT_SCI 201-0   ALL
MAT_SCI 301-0   ALL
PHYSICS 130-1   ALL
PHYSICS 135-1   ALL
PHYSICS 135-2   ALL
STAT    202-0   ALL
STAT    210-0   ALL
""".strip().split('\n')
classes = [" ".join(course.split()) for course in classes]
for c in classes:
  get_books_for_class(c.split(' '))

pprint(all_books)
