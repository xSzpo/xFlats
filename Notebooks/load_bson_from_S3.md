```python
import boto3
import bson
from bson.json_util import dumps, loads
import json

from PIL import Image
import PIL
from io import BytesIO
```


```python
s3 = boto3.resource('s3')
client = boto3.client('s3')
```


```python
bucket = s3.Bucket('31b179a9-539e-4d1d-9686-3136fe76b662')
```


```python
prefix = 'offers_bson_new/'
list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]

```


```python
list_files_in_offers_list
```


```python
file = client.get_object(Bucket='31b179a9-539e-4d1d-9686-3136fe76b662', Key=prefix+list_files_in_offers_list[1])['Body'].read()


```


```python
d=bson.BSON.decode(loads(file))
```


```python
d.keys()
```


```python
d
```


```python
def open_img_from_str(str_img):
    try:
        return Image.open(BytesIO(str_img))
    except BaseException:
        return None
```


```python
d['url']
```


```python
open_img_from_str(d['img_gallery_strimg'][0])
```
