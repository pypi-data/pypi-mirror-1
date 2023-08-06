###########
# helpers #
###########

def default(obj):
    return obj

def dicttolist(obj):
    return sorted([(x, y) for x, y in obj.iteritems()])

def listaddindex(obj):
    return zip(range(0, len(obj)), obj)

def classtolist(obj):
    return [("%s" % obj, vars(obj))]

def objtolist(obj):
    dic = vars(obj)
    temp = {}
    for k, v in vars(obj.__class__).iteritems():
        temp[k] = (k in dic and dic[k] or v)
    return [("%s" % obj, temp)]

def explored(t):
    return (t in (types.InstanceType, types.ClassType,
                 types.ListType, types.DictType))

###########
# print_r #
###########
import types

# depth
def print_r(obj=False, output = True, indent = 4, depth = 10):
    global TAB, MAXD
    if not obj:
        print "usage: print_r(object[, output[, indent[, depth]]])"
        return
    TAB = "".join([" " for x in range(0, indent)])
    MAXD = depth
    res = printtree(totree(obj))
    if output:
        print res
    return res

# make obj into a list
def totree(obj, depth = 0):
    if depth == MAXD:
        return "Max depth reached, change depth argument"
    tab = {types.InstanceType : objtolist,
           types.ClassType : classtolist,
           types.ListType : listaddindex,
           types.DictType : dicttolist}
    if type(obj) not in tab:
        return obj
    return [(x[0], totree(x[1], depth + 1), type(x[1]))
             for x in tab[type(obj)](obj)]

# print tree
def printtree(tree, tab = ""):
    if not (type(tree) is types.ListType):
        return tree
    return ((tab != "" and "\n" or "")
            +"\n".join([("%s%s = %s%s" %
                         (tab,
                          x[0],
                          explored(x[2]) and x[2] or "",
                          printtree(x[1], tab + TAB)))
                        for x in tree]))
