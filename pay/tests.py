from django.test import TestCase
import redis
from utils.redis_pool import POOL
import json

# Create your tests here.
conn =redis.Redis(connection_pool=POOL)
# conn.set('name1','alex')
# print(conn.get('name1'))
# c=conn.hgetall("shoping_car_1_1")
# print(c)
# conn.hmset("name2",{"age":json.dumps({'k1':'v1'},ensure_ascii=False)})
# print(conn.keys('*'))
# # conn.delete(*[])
# print(conn.get("account_1_1"))
def num():
    return [lambda x: i*x for i in range(4)]
print([m(2) for m in num()])
