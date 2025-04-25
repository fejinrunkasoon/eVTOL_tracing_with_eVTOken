# import xml.etree.ElementTree as ET

# tree = ET.parse('sec5_4.xml')
# root =tree.getroot()

# print("Root tag:",root.tag)

# for book in root.findall("book"):
#     book_id =book.get('id')
#     title = book.find('title').text
#     author =book.find('author').text
#     year =book.find('year').text
    
#     print(f"Book ID:{book_id}")
#     print(f"Title:{title}")
#     print(f"Author:{author}")
#     print(f"Year:{year}")
#     print("-"*20)

import json

with open('sec5_4.json','r') as file:
    data = json.load(file)
    
for book in data['library']:
    book_id =book['id']
    title = book['title']
    author = book['author']
    year =book['year']
    
    print(f'Book ID:{book_id}')
    print(f'Title:{title}')
    print(f'Author:{author}')
    print(f'Year:{year}')
    print('-'*20)