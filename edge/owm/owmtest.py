import owmforecast

print(owmforecast.getcurrent())
print(owmforecast.getforecast(0))
print(owmforecast.getnextrain())

# for i in range(5):
#     print(owmforecast.getforecast(i))

print(owmforecast.getforecast(0)['rain'])
