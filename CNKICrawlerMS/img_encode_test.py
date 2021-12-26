import ddddocr

ocr = ddddocr.DdddOcr()
with open('img/img_3.png', 'rb') as f:
    img_bytes = f.read()

res = ocr.classification(img_bytes)
for i in range(1,9):
    print(i)
