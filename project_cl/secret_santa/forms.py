from django import forms


CURRENCY_CHOICES = [
    ('USD', 'U.S. dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('JPY', 'Japanese yen (JPY)'),
    ('GBP', 'Sterling (GBP)'),
    ('CNY', 'Renminbi (CNY)'),
    ('AUD', 'Australian dollar (AUD)'),
    ('CAD', 'Canadian dollar (CAD)'),
    ('CHF', 'Swiss franc (CHF)'),
    ('HKD', 'Hong Kong dollar (HKD)'),
    ('SGD', 'Singapore dollar (SGD)'),
    ('SEK', 'Swedish krona (SEK)'),
    ('KRW', 'South Korean won (KRW)'),
    ('NOK', 'Norwegian krone (NOK)'),
    ('NZD', 'New Zealand dollar (NZD)'),
    ('INR', 'Indian rupee (INR)'),
    ('MXN', 'Mexican peso (MXN)'),
    ('TWD', 'New Taiwan dollar (TWD)'),
    ('ZAR', 'South African rand (ZAR)'),
    ('BRL', 'Brazilian real (BRL)'),
    ('DKK', 'Danish krone (DKK)'),
    ('PLN', 'Polish złoty (PLN)'),
    ('THB', 'Thai baht (THB)'),
    ('ILS', 'Israeli new shekel (ILS)'),
    ('IDR', 'Indonesian rupiah (IDR)'),
    ('CZK', 'Czech koruna (CZK)'),
    ('AED', 'UAE dirham (AED)'),
    ('TRY', 'Turkish lira (TRY)'),
    ('HUF', 'Hungarian forint (HUF)'),
    ('CLP', 'Chilean peso (CLP)'),
    ('SAR', 'Saudi riyal (SAR)'),
    ('PHP', 'Philippine peso (PHP)'),
    ('MYR', 'Malaysian ringgit (MYR)'),
    ('COP', 'Colombian peso (COP)'),
    ('RUB', 'Russian ruble (RUB)'),
    ('RON', 'Romanian leu (RON)'),
    ('PEN', 'Peruvian sol (PEN)'),
    ('BHD', 'Bahraini dinar (BHD)'),
    ('BGN', 'Bulgarian lev (BGN)'),
    ('ARS', 'Argentine peso (ARS)'),
]


class GameForm(forms.Form):
    max_price = forms.DecimalField(label='Max price', decimal_places=2, min_value=0.01)
    currency = forms.ChoiceField(label='Currency', choices=CURRENCY_CHOICES, widget=forms.Select)
