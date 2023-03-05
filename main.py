from bs4 import BeautifulSoup
import logging

logger = logging.getLogger()

if __name__ == "__main__":
    with open("./result/b5fcb4ad-6b42-4021-aefb-a030e662aacc/content.html", "r") as file:
        content = file.read()
      
    soup  = BeautifulSoup(content, "html.parser")

    print(len(soup.find_all("div", class_="Hotels__Wrapper")))