from fuzzywuzzy import fuzz
from jieba import posseg

stop = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'r']
text1 = "商务部：第二届进博会设立进口博览会发布平台中证网讯（记者 倪铭娅）商务部网站29日消息，中国国际进口博览会组委会办公室主任、商务部副部长王炳南在中外媒体吹风会上表示，第二届进博会活动更丰富，综合效应进一步放大。展会期间各类配套活动超过300场，增进国内外经济文化交流。设立进口博览会发布平台，权威解读中国重要政策，发布国际组织最新研究成果等。18个省区市将举办140多场非物质文化遗产和“中华老字号”交流展示活动。进口博览会集展览、交易、论坛、人文、外交等活动于一体，综合溢出效应不断放大。"
text2 = "进博会对中法合作具有特殊意义——访中国驻法国使馆经商处公使衔参赞高元元新华社巴黎10月28日电  专访：进博会对中法合作具有特殊意义——访中国驻法国使馆经商处公使衔参赞高元元"


def reduce(text):
    text = [x.word for x in posseg.lcut(text) if x.flag not in stop]
    text = "".join(text)
    return text


text1 = reduce(text1)
text2 = reduce(text2)

ret = fuzz.token_sort_ratio(text1, text2)
print(ret)

ret = fuzz.partial_token_sort_ratio(text1, text2)
print(ret)

ret = fuzz.token_set_ratio(text1, text2)
print(ret)
