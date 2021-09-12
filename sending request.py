#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests as r


# In[2]:


with open('test.html', 'r') as f:
        html: str = f.read()


# In[3]:


url = 'https://demo-qhaqywfuaq-oa.a.run.app/'
respond = r.post(url, data={ 'html': html})


# In[9]:


respond.status_code


# In[10]:


respond


# In[6]:


respond.json()['data']['content']


# In[ ]:





# In[ ]:




