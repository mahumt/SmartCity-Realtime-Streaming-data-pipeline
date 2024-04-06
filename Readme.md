<!-- https://freedium.cfd/https://blog.stackademic.com/building-a-smart-city-an-end-to-end-big-data-engineering-project-7a3d9a6ab104 -->

Use python 3.9  (download 3.9 to set up virtual env). 3.12 is finicky 
Create virtual environment: `py -3.10 -m virtualenv smartcity_env` 
Create docker-compose file


## To push to github
```
git remote -v
git remote add origin https://github.com/<user>/<user_repository>
git add .
git commit -m "updates to schema and sql files"
git push origin main
```