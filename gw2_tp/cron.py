from gw2_tp.gw2_update_and_alert import data_update
from gw2_tp.sending_notifications import notify


# test test
def my_cron_job():
    data_update()
    notify()
