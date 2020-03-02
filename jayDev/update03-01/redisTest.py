import redis, time

pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)

r = redis.Redis(connection_pool=pool)

# r.set(("Btri_"+"jay_abc"), "100.00", ex=2)
# print(r.get('Btri_jay_abc'))
# print(r.ttl('Btri_jay_abc'))
# time.sleep(3)
# print(r.get('Btri_jay_abc'))
# print(r.ttl('Btri_jay_abc'))
#
# r.hset("Q_jay_abc", 'stockprice', '200.00')
# print(r.hvals("Q_jay_abc"))
# r.delete("Q_jay_abc")
# r.hset("Q_jay_abc", 'stockname', 'abc')
# r.hset("Q_jay_abc", 'time', '1234567890')
# r.hset("Q_jay_abc", 'crypto', 'jfiejfio399493jfjj343lfe')
# r.expire("Q_jay_abc", 2)
# print(r.hvals("Q_jay_abc"))
# print(r.ttl("Q_jay_abc"))
# a = r.hvals("Q_jay_abc")
# print(a[0])
# time.sleep(3)
# print(r.ttl("Q_jay_abc"))

# r.rpush('jay', 'abc')
# r.rpush('jay', 'dfg')
# print(r.lrange('jay', 0, -1))
a = r.rpop('jay', ex, 10)
print(type(a))
# print(r.lrange('jay', 0, -1))
