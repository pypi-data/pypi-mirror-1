#===================================================================================#
#                                                 __                                #
#                                                /\ \__                             #
#                    _____   _ __   __  __    ___\ \ ,_\                            #
#                   /\ '__`\/\`'__\/\ \/\ \ /' _ `\ \ \/                            #
#                   \ \ \_\ \ \ \/ \ \ \_\ \/\ \/\ \ \ \_    __   __                #
#                    \ \  __/\ \_\  \/`____ \ \_\ \_\ \__\  /\_\ /\_\               #
#                     \ \ \/  \/_/   `/___/> \/_/\/_/\/__/  \/_/ \/_/               #
#                      \ \_\            /\___/                                      #
#                       \/_/            \/__/                                       #
#                                                                                   #
#===================================================================================#
#@copyright: 2008 by Jeremy Bouillanne
#@license: Apache Public Licence
__revision = '$Revision:  $'[11:-2]

def emphasis(txt):
    """
    >>> print emphasis("titatoum")
    *titatoum*
    """
    return "*"+txt+"*"
em=emphasis

def strong_emphasis(txt):
    """
    >>> print strong_emphasis("toto")
    **toto**
    >>> name,surname= "toto", "titi"
    >>> print strong_emphasis(name)+" -> "+strong_emphasis(surname)
    **toto** -> **titi**
    """
    return "**"+txt+"**"
strong=strong_emphasis

    
def interpreted_text(txt):
    """
    >>> print interpreted_text("the sun is shining")
    `the sun is shining`
    """
    return "`"+txt+"`"
it=interpreted_text

def inline_literal(txt):
    return "``"+txt+"``"
lit=inline_literal

def substitution_reference(txt):
    return "|"+txt+"|"
alias = substitution_reference

def substitution_definition(alias, inline_directive):
    return ".. |"+alias+"| "+inline_directive+"\n"
defalias = substitution_definition

def substitution_replace(alias, replaced_text):
    return substitution_definition(alias, "replace:: "+replace_text)

def substitution_image(alias, img):
    return substitution_definition(alias, "image:: "+img)

def inline_internal_target(txt):
    return "_`"+txt+"`"
target=inline_internal_target

def title(txt):
    return "=======================================\n"+txt+"\n=======================================\n"

def subtitle(txt):
    return txt+"\n-----------------------------------------------------------\n"

def paragraph(txt):
    return txt+"\n"
p=paragraph

def bullet_list(list):
    for k in range(len(list)):
        print "- "+list[k]+"\n"
    print
ul=bullet_list

__enumerated_count=1
def enumerated_list(list):
    for k in range(len(list)):
        global __enumerated_count
        print str(__enumerated_count)+". "+list[k]+"\n"
        __enumerated_count+=1
    print
ol=enumerated_list

def definition_list(dic):
    for k,v in dic.items():
        print k
        print "  "+str(v)+"\n"
    print
dl=definition_list

def field_list(dic):
    for k,v in dic.items():
        print ":"+k+":"
        print "  "+str(v)+"\n"
    print    
fl=field_list

def option_list():
    pass #@TODO write this function
optl=option_list

def literal_block(txt):
    return "::\n\n  "+txt #@TODO manage this function to handle multilines 
litb=literal_block 

def line_block(txt):
    return "| "+txt+"\n"
linb=line_block

def block_quote(txt, ind):
    return " "*ind+txt+"\n"
bq=block_quote 

def doctest_block(txt):
    return ">>> "+txt+"\n"
db=doctest_block 

def table(array):
    pass

def transition():
    return "--------\n"
tr=transition

def footnote_reference(type, txt=""):
    return "["+type+txt+"]_", ".. ["+type+txt+"]"
fref=footnote_reference

def hyperlink_reference(ref, url=None):
    if url!=None:
        return "`"+ref+" <"+url+">`_"
    else:
        return "`"+ref+"`_"   
href=hyperlink_reference

def comment(txt):
    return ":: "+txt+"\n" #@TODO make it working

def admonition(add, txt):
    return ".. "+add+"::\n   "+txt+"\n"
add=admonition

def image(img):
    return "\n.. image:: "+img+"\n"
img=image


def figure(fig):
    return ".. figure:: "+fig+"\n"
fig=figure

def topic(title, txt):
    return ".. topic:: "+title+"\n\n    "+txt+"\n"

def sidebar(title, txt, subtitle=""):
    side=".. sidebar:: "+title+"\n"
    if subtitle != "" : side+="   :subtitle: "+subtitle+"\n"
    side+="\n   "+txt+"\n"
    return side

def parsed_literal(txt):
    return ".. parsed-literal::\n\n   "+txt+"\n"

def rubric(txt):
    return ".. rubric:: "+txt+"\n"

def epigraph(txt, author):
    return ".. epigraph::\n\n   "+txt+"\n\n   -- "+author+"\n"

def highlights(txt):
    return ".. highlights:: "+txt+"\n"

def coumpound(txt, emb):
    return ".. compound::\n\n   "+txt+" ::\n\n       "+emb+"\n"

def container(txt, type="custom"):
    return ".. container:: "+type+"\n\n   "+txt+"\n"
div=container






def custom_role(role, interpreted_text):
    return ":"+role+":"+"`"+interpreted_text+"`"


