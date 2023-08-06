from collective.feedfiller.filler import Filler

filler = Filler()

def feedItemArrivedHandler(event):
    item = event.object
    filler.fill(item)
            
