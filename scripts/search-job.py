# Submits search job, waits for completion, then prints and emails results.
# Pass the query via stdin.
#
# cat query.sumoql | python search-job.py <accessId/email> <accessKey/password> \
# <fromDate> <toDate> <timeZone>
#
# Note: fromDate and toDate must be either ISO 8601 date-times or epoch
#       milliseconds
#
# Example:
#
# cat query.sumoql | python search-job.py <accessId/email> <accessKey/password> \
# 1408643380441 1408649380441 PST

import json
import sys
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from sumologic import SumoLogic

LIMIT = 42

args = sys.argv
sumo = SumoLogic(args[1], args[2])
fromTime = args[3]
toTime = args[4]
timeZone = args[5]

delay = 2
q = ' '.join(sys.stdin.readlines())
sj = sumo.search_job(q, fromTime, toTime, timeZone)

status = sumo.search_job_status(sj)
while status['state'] != 'DONE GATHERING RESULTS':
    if status['state'] == 'CANCELLED':
        break
    time.sleep(delay)
    delay *= 2
    status = sumo.search_job_status(sj)

print status['state']

if status['state'] == 'DONE GATHERING RESULTS':
    count = status['recordCount']
    limit = count if count < LIMIT else LIMIT # compensate bad limit check
    r = sumo.search_job_records(sj, limit=limit)
    print r
