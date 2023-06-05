# FBAR Max Balances Generator

The Foreign Bank Account Report (FBAR) is form that must be filed by all US citizens who hold foreign accounts holding at least $10,000. When filing this report, one must supply the maximum balance for each foreign account for a given year. This Python script utilizes the YNAB API to generate the maximum balance for each account for a user for a given calendar year. 

## Dependencies

* prettytable
* pyyaml
* ynab==0.0.3

## Usage

1. Generate a [YNAB Personal Access Token](https://api.youneedabudget.com/#personal-access-tokens).
2. Copy [example-config.yml](example-config.yml) to a new config.yml file to add your token as well as the 
   relevant year and [currency conversion rate](https://www.irs.gov/individuals/international-taxpayers/yearly-average-currency-exchange-rates).
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Run main script:
```
python main.py
```
A report, like the one below, will be generated.

```+------------------------------------------------------------+-----------------+-----------------+------------+------------+
|                            Name                            | Max Balance EUR | Max Balance USD | Start Date |  End Date  |
+------------------------------------------------------------+-----------------+-----------------+------------+------------+
|                     Deutsche Kreditbank                    |     €214.32     |     $253.33     | 2021-07-17 | 2021-07-17 |
|                            ING                             |     €2651.48    |     $3134.14    | 2021-02-01 | 2021-02-01 |
|                            N24                             |     €1414.73    |     $1672.26    | 2021-12-01 | 2021-12-15 |
```

## Future Ideas
- [ ] Support more currencies.
- [ ] Autodetect account currency.
- [ ] Interactive script to exclude accounts.
- [ ] Enrich accounts with other relevant FBAR data.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
