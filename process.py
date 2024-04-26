import csv
from pygrok import Grok

import gspread


gc = gspread.service_account()
sh = gc.open("grokker-dataset")


def read_grok_csv():
    prev = ""
    with open("android.csv", "r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if prev == row:
                continue
            try:
                grok = Grok(row[1])
                grok_match = grok.match(row[0])
                print(grok_match)
                if grok_match:
                    print("Appending to sheet")
                    sh.sheet1.append_row(
                        [row[0], row[1], str(grok_match)])
            except:
                pass
            prev = row


def verify_grok():
    log_line = "[Sun Jan 22 21:45:40 2006] [error] [client 64.182.1.110] File does not exist: /var/www/html/awstats/awstats.pl"
    grok_pattern = "\\[%{DAY:day} %{MONTH:month} %{MONTHDAY:monthday} %{TIME:time} %{YEAR:year}\\] \\[%{WORD:loglevel}\\] \\[client %{IP:client_ip}\\] %{GREEDYDATA:error_message}: %{GREEDYDATA:file_path}"
    grok = Grok(grok_pattern)
    grok_match = grok.match(log_line)
    print(grok_match)


if __name__ == "__main__":
    verify_grok()
