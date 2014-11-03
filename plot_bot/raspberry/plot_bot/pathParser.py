d="M120.864,156.202c0.599,0.816-1.205,3.568-1.205,3.568l-3.008,1.953l-4.702-2.664l-3.678-7.749"
#d="M128.359,173.468h77.16 M205.52,188.858h-77.16"
ds=d.replace("c", " c ").replace("l", " l ").replace("-", " -").replace(",", " ").replace("M", "M ").replace("h", " h ")
print ds
ss=ds.replace("  ", " ").split(" ")
print ss

ptr=0
state=""
curvecnt=0 # todo: Bezier Curve
while ptr<len(ss):
    #print "parse",ss[i]
    if ss[ptr].isalpha():
        print "into state",ss[ptr]
        state = ss[ptr]
        ptr+=1
    else:
        if state=="h":
            dis=ss[ptr]
            print "h",dis
            ptr+=1
        elif state=="v":
            dis=ss[ptr]
            print "v",dis
            ptr+=1
        else:
            x=ss[ptr]
            y=ss[ptr+1]
            ptr+=2
            print "x",x,"y",y
