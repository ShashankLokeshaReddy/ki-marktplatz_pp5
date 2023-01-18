import pandas as pd
from django.core.management.base import BaseCommand
from machines.models import Machine
#from sqlalchemy import create_engine
from django.conf import settings

#def formatcsv(df):

class Command(BaseCommand):
    
    def handle(self, *args, **options):
    #We only keep the rows necessary to us
        df = pd.read_csv("../data/Auftragsfolgen-20211207.csv")

        df = df[['MaschNr','Start', 'Ende', 'KndNr', 'AKNR','SchrittNr']]

        #Deleting the unnecessary endings for the SL and FKM identifiers

        df.replace(regex=r'^SL 2.*', value='SL 2', inplace=True)
        df.replace(regex=r'^SL 4.*', value='SL 4', inplace=True)
        df.replace(regex=r'^SL 5.*', value='SL 5', inplace=True)
        df.replace(regex=r'^SL.6.*', value='SL 6', inplace=True)
        df.replace(regex=r'^SL.7.*', value='SL 7', inplace=True)
        df.replace(regex=r'^SL.8.*', value='SL 8', inplace=True)
        df.replace(regex=r'^SL.9.*', value='SL 9', inplace=True)
        df.replace(regex=r'^SL.10.*', value='SL 10', inplace=True)
        df.replace(regex=r'^SL 11.*', value='SL 11', inplace=True)
        df.replace(regex=r'^FKM.*', value='FKM', inplace=True)

        #Deleting the rows which do not contain any of the SL or FKM identifiers
        
        df = df[df["MaschNr"].str.contains("SL 2|SL 4|SL 5|SL 6|SL 7|SL 8|SL 9|SL 10|SL 11|FKM") == True]
        df = df.dropna()
        df.rename(columns={'MaschNr':'resourceId'}, inplace=True)
        df = df.head(n=250000)#, if you want to take the first n rows of the dataset
        
        print(df)
        df.to_csv('Auftragsplanung_kompremiert.csv')

        #Code which was used trying to directly import the csv into the db with this script. Did not work and threw no error
        #user = settings.DATABASES['default']['USER']
        #password  = settings.DATABASES['default']['PASSWORD']
        #database_name = settings.DATABASES['default']['NAME']
        #database_url = 'postgresql://{user}:{password}@0.0.0.0:8000/{database_name}'.format(user=user, password=password,
        #database_name=database_name,)
        #print('2')
        #engine = create_engine(database_url, echo=False)
        #print('3')
        #the following peace of code did not finish and threw no error
        #df.to_sql(Machine, if_exists ='replace', con=engine, index=True)
        #print('4')
        #if __name__ == "__main__":
        #    df = pd.read("data/results_transformed_new.csv")
        #    formatcsv(df)
            