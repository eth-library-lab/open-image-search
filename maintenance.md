## naming convention

**field/column names**: all  in tables are in **snake_case** *e.g. author_name*  
**models**: all models are in **CamelCase** in singular form (no plurals).  *e.g. a model defing a table for records of books is class Book(models.Model):*  
**urls**: endpoints for models are in **kebab-case** in singular form e.g.: *the model DisorderCategory has the url disorder-category* 


## Renew ssl certificates
tags: `ssl certbot let's encrypt`

stop nginx container

```
docker stop graph-samm_web_1
```

renew certifcate using certbot
```
sudo certbot renew
```
restart nginx container
```
docker restart graph-samm_web_1
```