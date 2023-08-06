##parameters=obj

view = obj.restrictedTraverse('@@rss2', None)
if view is not None:
    return view()
return ''
