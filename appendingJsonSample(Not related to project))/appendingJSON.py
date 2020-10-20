import pandas as pd
import json
data_1 = {
    "id":1,
    "key":"vbkhcbkdscnjkbvchadscebjl"
}
data_2 = {
    "id":2,
    "key":"cnxksafhnaldcmladsnvjkascxlm"
}
data_3 = {
    "id": 3,
    "key": "cnxkasdasxsaxsafhnaldcmladsnvjkascxlm"
}

df = pd.DataFrame()
df = df.append(data_1,ignore_index=True)
df = df.append(data_2,ignore_index=True)
print(df)
df.to_csv("junk.csv",index=False)

df = pd.read_csv("junk.csv")
df = df.append(data_3,ignore_index=True)
print(df)
print(df['id'])
print(df.loc[1])
df.to_csv("junk.csv", index=False)
