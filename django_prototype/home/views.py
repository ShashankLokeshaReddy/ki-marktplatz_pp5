from django.http import HttpResponse
from django.template import loader
import arise_prototype.capacity_check as capacity_check
import pandas as pd


# Create your views here.
def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))


def test_api(request):
    # rufe get capacities auf --> Tabelle
    # request enthält irgendwie Datum
    selected_date = request.GET['date']

    print(selected_date)
    # template = loader.get_template('home/production_info_table.html')
    print('loading data')
    start = pd.to_datetime(selected_date, format='%Y-%m-%d')
    end = start + pd.Timedelta(6, "d")
    data, df_workload = capacity_check.run_frozen_zone_definition(start, end)
    print('data loaded')
    html = data.to_html()

    # return JsonResponse({"selected_date": selected_date})
    # return HttpResponse(template.render({}, request))
    return HttpResponse(html)
