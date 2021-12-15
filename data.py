import pandas as pd
from datetime import date
from datetime import timedelta
from datetime import datetime, timezone
import numpy as np
from math import floor, ceil
conditions = ["confirmed", "deaths", "recovered"]

today = date.today()
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')
two_days_ago = today - timedelta(days=2)
two_days_ago = two_days_ago.strftime('%Y-%m-%d')
two_days_ago_url = today - timedelta(days=2)
two_days_ago_url = two_days_ago_url.strftime('%m-%d-%Y')
now_utc = datetime.now(timezone.utc).strftime('%H')
#now_here = datetime.now().strftime('%H')

if now_utc > '06':
    daily_url = f'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/{yesterday}.csv?raw=true'
else:
    daily_url = f'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/{two_days_ago_url}.csv?raw=true'


daily_df = pd.read_csv(daily_url)
countries_df = daily_df[["Country_Region", "Confirmed", "Deaths"]]

countries_df = (countries_df.groupby("Country_Region").sum(
).sort_values(by="Confirmed", ascending=False).reset_index())


pop_url = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv?raw=true'
pop_df = pd.read_csv(pop_url)
pop_df = pop_df[(pop_df['Province_State'].isnull())]
pop_df = pop_df[["Country_Region", "Population", "iso3"]]

continent_url = 'https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv?raw=true'
continent_df = pd.read_csv(continent_url)
continent_df = continent_df[["alpha-3", "region", "sub-region"]]
continent_df = continent_df.rename(columns={'alpha-3': 'iso3'})
pop_df = pd.merge(pop_df, continent_df, on="iso3")

countries_df = pd.merge(countries_df, pop_df, on="Country_Region")

daily_time_url = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv?raw=true'
daily_time_df = pd.read_csv(daily_time_url)
daily_time_df = daily_time_df.drop(["Lat", "Long"], axis=1)

daily_time_df_AuCaCh = daily_time_df.dropna(subset=['Province/State'])
daily_time_df_AuCaCh = daily_time_df_AuCaCh.groupby("Country/Region").sum()
daily_time_df_AuCaCh = daily_time_df_AuCaCh.loc[[
    'Australia', 'Canada', 'China'], :]
daily_time_df_AuCaCh = daily_time_df_AuCaCh.reset_index()
daily_time_df = daily_time_df[(daily_time_df['Province/State'].isnull())]
daily_time_df = daily_time_df.drop(["Province/State"], axis=1)

daily_time_df = daily_time_df.append(daily_time_df_AuCaCh, ignore_index=True)
daily_time_df = daily_time_df.iloc[:, list(range(1)) + list(range(-8, 0))]
daily_time_df["Cases_in_last_7_days"] = (
    daily_time_df.iloc[:, -1] - daily_time_df.iloc[:, -8])
daily_time_df["Yesterday_Confirmed"] = (
    daily_time_df.iloc[:, -2] - daily_time_df.iloc[:, -3])
daily_time_df = daily_time_df.iloc[:, list(range(1)) + list(range(-2, 0))]
daily_time_df = daily_time_df.rename(
    columns={'Country/Region': 'Country_Region'})
countries_df = pd.merge(countries_df, daily_time_df,
                        on="Country_Region", how='inner')
countries_df["7_Days_Incidence_Rate"] = (
    countries_df["Cases_in_last_7_days"] / (countries_df["Population"]/100000))

vac_url = 'https://github.com/govex/COVID-19/blob/master/data_tables/vaccine_data/global_data/vaccine_data_global.csv?raw=true'
df_vaccine = pd.read_csv(vac_url)
df_vaccine = df_vaccine[(df_vaccine['Province_State'].isnull())]
df_vaccine = df_vaccine[["Country_Region", "People_fully_vaccinated"]]

countries_df = pd.merge(countries_df, df_vaccine,
                        on="Country_Region", how='inner')
countries_df = countries_df.sort_values(
    by="7_Days_Incidence_Rate", ascending=False)
countries_df['Population'] = countries_df['Population'].astype(int)
countries_df['7_Days_Incidence_Rate'] = countries_df['7_Days_Incidence_Rate'].astype(
    int)


vac_owid_url = 'https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/vaccinations.csv?raw=true'
df_vac_owid = pd.read_csv(vac_owid_url)
df_vac_owid = df_vac_owid[["location", "date", "people_fully_vaccinated"]]
df_vac_owid = df_vac_owid.loc[df_vac_owid["date"] == two_days_ago]
df_vac_owid_south_korea = df_vac_owid.loc[df_vac_owid["location"]
                                          == "South Korea"]
df_vac_owid_south_korea = df_vac_owid_south_korea[["people_fully_vaccinated"]]

loc_korea_vac_cell = countries_df.loc[countries_df.index[countries_df["Country_Region"]
                                                         == "Korea, South"], 'People_fully_vaccinated'].item()
if pd.isnull(loc_korea_vac_cell) is True:
    countries_df[countries_df["Country_Region"] == "Korea, South"] = countries_df[countries_df["Country_Region"] == "Korea, South"].replace(to_replace=np.nan,
                                                                                                                                            value=df_vac_owid_south_korea.iat[0, 0])
else:
    pass

countries_df[countries_df.isna().any(axis=1)]
countries_df = countries_df.dropna()
countries_df['People_fully_vaccinated'] = countries_df['People_fully_vaccinated'].astype(
    'Int64')


countries_df["Fully_vaccinated_percent"] = (
    countries_df["People_fully_vaccinated"] / (countries_df["Population"]))*100
countries_df['Fully_vaccinated_percent'] = countries_df['Fully_vaccinated_percent'].astype(
    'float64')
countries_df['Fully_vaccinated_percent'] = countries_df['Fully_vaccinated_percent'].apply(
    lambda x: round(x, 2))
####################
top10_table = countries_df.head(10)
top10_table = top10_table[["Country_Region", "7_Days_Incidence_Rate"]]
top10_table = top10_table.rename(columns={'Country_Region': 'Country'})
top10_table

#########
totals_df = countries_df[["Confirmed", "Deaths",
                          "People_fully_vaccinated"]].sum().reset_index(name="count")
totals_df = totals_df.rename(columns={'index': "condition"})

df_pop_sum = pd.DataFrame(
    {
        "condition": ["Population"],
        "count": [7794592576.0]
    }
)

totals_df = totals_df.append(df_pop_sum, sort=False)  # 7794592576.0
totals_df = totals_df.reset_index()
totals_df = totals_df.drop('index', 1)
totals_df['count'] = totals_df['count'].astype('Int64')
totals_df
totals_df_bar = totals_df.iloc[2:4]
####

#######
df_pop = pd.read_csv("data/population.csv")
# https://worldpopulationreview.com/
df_pop_countries = df_pop[["name", "pop2020"]]
df_pop_countries["pop2020"] = 1000 * df_pop_countries["pop2020"]
df_pop_countries = df_pop_countries.rename(
    columns={'pop2020': 'Population (2020)'})

df_pop_sum = df_pop_countries.sum().reset_index(name="count")
df_pop_sum = df_pop_sum.rename(columns={'index': 'condition'})
df_pop_sum = df_pop_sum.iloc[1:]

######
vac_url = 'https://github.com/govex/COVID-19/blob/master/data_tables/vaccine_data/global_data/vaccine_data_global.csv?raw=true'
df_vaccine = pd.read_csv(vac_url)
df_vaccine = df_vaccine[["Country_Region", "Date", "People_fully_vaccinated"]]
df_vaccine_world = df_vaccine[df_vaccine["Country_Region"] == "World"]
df_vaccine_world = df_vaccine_world[["People_fully_vaccinated"]]
df_vaccine_world = df_vaccine_world.rename(
    columns={'People_fully_vaccinated': 'count'})
df_vaccine_world.insert(0, "condition", ["Fully vaccinated"], True)


###
dropdown_options = countries_df.sort_values("Country_Region").reset_index()
dropdown_options = dropdown_options["Country_Region"]


def make_country_confirmed_df(country):
    url_time_confirmed = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv?raw=true'
    df = pd.read_csv(url_time_confirmed)
    df = df.loc[df["Country/Region"] == country]
    df = df.drop(columns=["Province/State", "Country/Region",
                 "Lat", "Long"]).sum().reset_index(name="Confirmed")
    df = df.rename(columns={"index": "date"})
    return df


def make_country_death_df(country):
    url_time_death = url = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv?raw=true'
    df = pd.read_csv(url_time_death)
    df = df.loc[df["Country/Region"] == country]
    df = df.drop(columns=["Province/State", "Country/Region",
                 "Lat", "Long"]).sum().reset_index(name="Death")
    df = df.rename(columns={"index": "date"})
    return df

 ###############


def make_global_confirmed_df():
    url_time_confirmed = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv?raw=true'
    time_confirmed_df = pd.read_csv(url_time_confirmed)
    time_confirmed_df = (
        time_confirmed_df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1)
        .sum()
        .reset_index(name="Confirmed")
    )
    time_confirmed_df = time_confirmed_df.rename(columns={"index": "date"})
    return time_confirmed_df


def make_global_death_df():
    url_time_death = url = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv?raw=true'
    time_death_df = pd.read_csv(url_time_death)
    time_death_df = (
        time_death_df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1)
        .sum()
        .reset_index(name="Death")
    )
    time_death_df = time_death_df.rename(columns={"index": "date"})
    return time_death_df
####
