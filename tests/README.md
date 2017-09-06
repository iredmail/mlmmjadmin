# Unit tests for mlmmj-admin RESTful API

## Requirements

* Python module `pytest`: <https://pytest.org>
* For iRedMail users:
    * If you use backend `bk_iredmail_*`, please create new mail domain
      `api-test.com` with iRedAdmin manually first

## Run the tests

* Run shell script `main.sh`:

```
cd tests/
bash main.sh
```

* For iRedMail users, please remove domain `api-test.com` with iRedAdmin manually.
