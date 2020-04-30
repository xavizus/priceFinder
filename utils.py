import re

def remove_html_tags(text: str) -> str:
    clean = re.compile(r'<.*?>')
    return re.sub(clean,'', text)

def remove_white_space(text: str) -> str:
    clean = re.compile(r'\s+')
    return re.sub(clean, '', text)