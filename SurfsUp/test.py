from sqlalchemy import create_engine, func, null
from datetime import datetime
import datetime as dt
from sqlalchemy import cast, Date
start_date = "2014-04-21"
inclusive_start = datetime.strptime(start_date, "%Y-%m-%d") - dt.timedelta(days=1)
print(inclusive_start)