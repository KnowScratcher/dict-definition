from bs4 import BeautifulSoup

HTML_DOC = """ 
                    <p class = "languages">1957: FORTRAN</p> 
  
                    <p class = "languages">1972: C</p> 
  
                    <p class = "languages">1983: C++</p> 
  
                    <p class = "languages">1991: Python</p> 
  
                    <p class = "languages">1993: Ruby</p> 
  
                    <p class = "languages">1995: Java</p> 
  
                    <p class = "languages">1995: PHP</p> 
  
                    <p class = "languages">1995: JavaScript</p> 
            """

soup = BeautifulSoup(HTML_DOC, "html5lib") 
print(soup.find("p"))