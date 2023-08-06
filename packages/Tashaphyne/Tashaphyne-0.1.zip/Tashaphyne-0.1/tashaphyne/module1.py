#testnormlalize
from normalize import *
word=u"تـــاشــفــين"
newword=strip_tatweel(word)
print newword
word=u"الْعَرَبِيّةُ"
print strip_tashkeel(word)
text=u"لأنها لآلئ الإسلام"
text=normalize_lamalef(text)
print normalize_hamza(text);
text=u'اشترت سلمى دمية وحلوى'
print normalize_spellerrors(text);
##أستشتري دمـــى آلية لأبنائك قبل الإغلاق
text=u'أستشتري دمـــى آلية لأبنائك قبل الإغلاق'
print normalize_searchtext(text);
