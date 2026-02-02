# datatrans


https://pay.sandbox.datatrans.com/v1/start/transactionId



datatrans-python/
├── datatrans/
│   ├── __init__.py
│   ├── client.py          # Main API client
│   ├── exceptions.py      # Custom exceptions
│   ├── models.py          # Data models/Pydantic schemas
│   ├── webhook.py         # Webhook verification
│   └── utils.py           # Helper functions
└── datatrans/
    └── contrib/
        └── djdatatrans/
            ├── __init__.py
            ├── apps.py
            ├── models.py
            ├── views.py
            ├── urls.py
            └── templatetags/
                └── datatrans_tags.py