import louie
from louie import dispatcher
from louie import Any

class reciever_test(object):
    def __call__(self,data="tutu",pouet=2,*args,**kwargs):
        print("data",data)
        print("pouet",pouet)
        print("args",args)
        print("kwargs",kwargs)

class emmiter_test(object):
    pass

if __name__ == "__main__":
    e=emmiter_test()
    r=reciever_test()
    louie.connect(r, signal="doboz_web.task", sender=Any, weak=True)
    namedArgs={'data':44}
    err=louie.send("doboz_web.task", e,pouet="oh no",data=44,arguments=None)
    print("err",err)
