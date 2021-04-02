# Auer_B_Telegram_Bot

## Dev setup

1. Install python-dev on os

### rhel7
2. yum install python36-devel.x86_64

3. Create a virtualenv 
```bash
python -m pip install virtualenv
python -m virtualenv venv
```
4. Install project dependencies 
```bash
python -m pip install -r requerments.txt 
``` 
5. Install development dependencies
```bash
python -m pip install -r dev-requerments.txt 
```
6. Install the pre-commit hooks
```bash
pre-commit install
```


### Runing unit tests

```bas 
python -m pytest .\tests
```  

  
### How to start Auer_B_Telegram_Bot
