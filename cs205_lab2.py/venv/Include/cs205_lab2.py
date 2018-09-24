class doggy:
    name=""
    def __init__(self,input_name):
       self.name=input_name
    def bark(self):
        return self.name+' '+'bark'
def hello_world():
    print("Hello World")
def find_prime(start:int,end:int) -> list:
    prime_list = []
    for i in range(start,end+1):
        sqrt_num=int(i**0.5)
        for j in range(2,sqrt_num+1):
            if i%j==0:
               break
        else:
            prime_list+=[i]
    return prime_list
def printer_maker(key) :
    def find_key(tag_dic:dict):
        return tag_dic[key]
    return find_key

hello_world()
print(find_prime(3,25))
dog=doggy("mydog")
print(dog.bark())
fun= printer_maker("1")
adic = {"1":"qie","2":"zhang"}
print(fun(adic))