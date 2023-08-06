import sys
import pygments
import pygments.lexers as lexers

f = open(sys.argv[1])
txt = f.read()
f.close()

l = lexers.get_lexer_by_name('d')

for tok in l.get_tokens_unprocessed(txt):
    print tok
