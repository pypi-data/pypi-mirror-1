for i in range(0, 10):
    f = open("file-%d" % i, "wb")
    f.write("1234567890" * 100)
    f.close()
