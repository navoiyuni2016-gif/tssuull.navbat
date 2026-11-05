"""User-selected Uzbek alphabet: Sh/Ch/G‘/O‘ -> Ş/Ç/Ğ/Ö."""
import re


def text(value):
    if not isinstance(value,str):return value
    value=re.sub(r"([oOgG])['‘’ʻʼ`\u02bb]",lambda m:{'o':'ö','O':'Ö','g':'ğ','G':'Ğ'}[m[1]],value)
    value=re.sub('sh|ch',lambda m:{'sh':'ş','ch':'ç'}[m[0].lower()].upper() if m[0][0].isupper() else {'sh':'ş','ch':'ç'}[m[0].lower()],value,flags=re.I)
    return value
