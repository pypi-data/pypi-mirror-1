#testnormlalize
from stemming import *

print newword
word=u"الْعَرَبِيّةُ"
ArListem=ArabicLightStemmer();
stem=ArListem.lightStem(word);

print ArListem.get_unvocalized();
word=u'أفتكاتبانني'
stem=ArListem.lightStem(word);
print ArListem.get_stem();
print ArListem.get_right();


ArListem=ArabicLightStemmer();
word=u'فتصربين'
stem=ArListem.segment(word);
print ArListem.get_affix_list();
print ArListem.get_segment_list();
