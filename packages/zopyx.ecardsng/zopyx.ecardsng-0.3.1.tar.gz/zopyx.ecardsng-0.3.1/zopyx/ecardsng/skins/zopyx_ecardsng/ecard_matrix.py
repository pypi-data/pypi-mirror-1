##parameters=images, cols

# return a nested list of lists to render images as a table
# with 'cols' columns

lst = []
num_images = len(images)
for i in range(0, (num_images + cols) / cols):

    l = list()
    for j in range(0, cols):
        idx = i*cols + j
        if idx < num_images:
            l.append(images[idx])
        else:
            l.append(None)
    lst.append(l)
return lst
