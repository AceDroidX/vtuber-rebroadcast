streamID={}

def manualAdd(name,id):
    streamID[name]=id
    
def manualDel(string):
    if string in streamID:
        streamID.pop(string)
    else:
        for name,id in streamID.items():
            if string==id:
                streamID.pop(name)