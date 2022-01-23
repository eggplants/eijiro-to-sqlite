# eijiro-to-sqlite

英辞郎 Ver.144.8 ( https://booth.pm/ja/items/777563 ) -> sqlite3

## Screenshot

![img](https://user-images.githubusercontent.com/42153744/150694352-5f0af040-a79b-4e12-bd21-40ed67068a57.png)


## Run

```bash
python parse_eijiro_to_sqlite.py
```

## Schema

```sql
CREATE TABLE word (
    id integer primary key,
    word text,
    meaning text,
    descriptions text
)
```
