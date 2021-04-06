from requests import get
from pprint import pprint
import time
import traceback
import send_metrics_to_telegraf
import get_env
import get_env_app

# artifacts (metminifuncs)
import sync_start_time


def get_data(url):
    try:
        response = get(url, timeout=30)

        # if response.status_code >= 400:
        #     raise RuntimeError(f'Request failed: { response.text }')

        return response.json()

    except Exception as e:
        print(e.__str__())
        return None


def main():
    england_endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=nation;areaName=england&structure={"date":"date", "areaName":"areaName", "areaCode":"areaCode", "newCasesByPublishDate":"newCasesByPublishDate", "cumCasesByPublishDate":"cumCasesByPublishDate", "newDeathsByDeathDate":"newDeathsByDeathDate", "cumDeathsByDeathDate":"cumDeathsByDeathDate"}'
    )
    version = get_env.get_version()
    verbose = get_env.get_verbose()
    stage = get_env.get_stage()
    poll_secs = get_env_app.get_poll_secs()
    telegraf_endpoint_host = get_env.get_telegraf_endpoint()  # can be read from ENV

    print('cv19d started, version=' + version)
    print('stage=' + get_env.get_stage())
    if stage == 'DEV':
        verbose = True
    print('verbose=' + verbose.__str__())
    print('telegraf_endpoint_host=' + telegraf_endpoint_host)
    print('poll_secs=' + poll_secs.__str__())

    while True:
        try:
            print('waiting to sync main loop...')
            sync_start_time.wait_until_minute_flip(30)      # every 30 minutes
            start_secs = time.time()
            data = get_data(england_endpoint)

            if data is None:
                time.sleep(180)

            yesterdays_data = data['data'][1]
            # pprint(yesterdays_data)

            metrics = {
                'metric_name': 'covid19',
                'newDeaths': yesterdays_data['newDeathsByDeathDate'],
                'newCases': yesterdays_data['newCasesByPublishDate']
            }

            print(time.ctime())
            pprint(metrics)

            send_metrics_to_telegraf.send_metrics(telegraf_endpoint_host, metrics, verbose)

            stop_secs = time.time()
            mins_between_updates = 30
            sleep_secs = (mins_between_updates * 60) - (stop_secs - start_secs) - 10
            time.sleep(sleep_secs)

        except Exception as e:
            print('Error : ' + e.__str__())
            traceback.print_exc()
            time.sleep(60)
            continue


if __name__ == '__main__':
    main()


