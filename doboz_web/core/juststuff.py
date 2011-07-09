

def truc():
    f=file("test.gcode","r")
    #line=f.next()
    for line in f:
        print(line)
    
    f.close()
    
if __name__=="__main__":
    truc()