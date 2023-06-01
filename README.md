# Инструкция по работе со скрапером

## Разворачиваем локально

Убедиться, что на установлен python3.8

Рекомендую использовать (pyenv)[https://github.com/pyenv/pyenv], т.к. на нем построено все в облаке. Да и вообще, полезная штука

Для того, чтобы установить python3.8.10 с помощью pyenv, 

```shell
pyenv install 3.8.10
```

После этого в директории с проектом автоматически будет использоваться нужная версия питона. Она указана в файле .python-version

```shell
cd travel_scraper
python --version
```

Должно выдать 3.8.10

Для сборки проекта используется poetry. Рекомендую установить его в какой-нибудь внешний питон

```shell
pip install poetry
```

Возможно придется добавить команду poetry в PATH - через .bash_profile, .zprofile, .zsh_profile (чтобы команда была доступна при перезагрузке терминала)

Дальше все просто. Переходим в проект, и устанавливаем окружение

```shell
cd travel_scraper
poetry install
```

Вуаля, окружение готово

Запуск любых команд в окружении можно делать с помощью poetry run

Например, запуск тестового файла (main.py) в этом окружении

```shell
poetry run python main.py
```

## Настройка Selenium и интеграции с облаком

Для того, чтобы работать, нужно установить драйвер Chrome и браузер Chrome

Как это сделать - можно найти в Интернете

После этого нужно создать файл с секретами secrets.sh

```bash
export CHROME_PATH="/usr/bin/chromedriver"
export AWS_ACCESS_KEY_ID="******"
export AWS_SECRET_ACCESS_KEY="*****"
export AWS_ENDPOITNT_URL="https://storage.yandexcloud.net"
export AWS_REGION_NAME="********"
export AWS_BUCKET="*******"
```

CHROME_PATH - путь к драйверу хрома, выглядит примерно так, но может отличаться
Остальное  - секреты для доступа к S3 - нужно запросить у меня

Далее для запуска чего-либо предварительно нужно добавить переменные в окружение

```bash
source secrets.sh
```

## Разработка

Здесь все стандартно, создаем свою ветку, пилим свои изменения

Наиболее вероянтный сценарий - новый парсер

Соответственно добавляем новый файл parser.py (вместо parser - название)

Главное что нужно добавить в файл - функция parse_with_params


```python
@add_meta("https://website.co")
def parse_with_params(browser: webdriver.Chrome, *, country_code: str, nights: str, debug: bool = False):
    some_stat = {"url": "final_url.com"}
    return browser.page_source, some_stat
```

browser - инстанс браузера селениума (он же иногда называется driver)


country_code: str, nights: str - параметры парсинга

debug: bool - переменная, которая отвечает за режим дебага. Обычно в таком режиме браузер никуда не скроллит, просто выполняет какие-то минимальные действия, чтобы убедиться, что все работает

browser.page_source - собственно самая HTML-страница

some_stat - словарь с любой информацией дополнительной, которую хочется сохранить. Рекомендую сохранять туда отформатированную url, по которой выполнялся запрос

Второе, что нужно добавить в файл - функция grid_option - которая превращает параметры из конфигурации в grid_option

Для чего это сделано - для того, чтобы добавлять кастомные настройки в сетку (например, задавать шаги, определять зависимые параметры)

Если не хочется заморачиваться, просто добавляем стандартную функцию

```python
def grid_option(grid_config: dict) -> list:
    grid = create_grid(grid_config)

    return grid
```


Такая функция превратит конфигурацию сетки
```python
grid_config = {
    "num_nights": [5, 6,],
    "country": ["UAE", "Thailand"]
}
```

В готовую сетку (то есть выполняется декартово произвденеи в конфигурации)

```python
grid = grid_option(grid_config)
grid = [
    {"num_nights" : 5, "country" : "UAE"},
    {"num_nights" : 5, "country" : "Thailand"},
    {"num_nights" : 6, "country" : "UAE"},
    {"num_nights" : 6, "country" : "Thailand"},
]
```

Для целей предварительного тестирования в файле scraper.py закоментить dump_result_and_meta_s3 и откоментить dump_result_and_meta

Результаты будут сохраняться локально

Хорошо, все готово, теперь добавляем конфигурацию с названием своего парсера в config.yaml

И запускаем парсер

```bash
poetry run run_selenium --parser <your-parser> 
```

Готово

## Deployment

Делаем pull-request, пишем мне указывваем какую строчку в конфиге деплоить




