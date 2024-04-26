from pygrok import Grok


def verify_grok():
    log_line = "[Sun Jan 22 21:45:40 2006] [error] [client 64.182.1.110] File does not exist: /var/www/html/awstats/awstats.pl"
    grok_pattern = "\\[%{DAY:day} %{MONTH:month} %{MONTHDAY:monthday} %{TIME:time} %{YEAR:year}\\] \\[%{WORD:loglevel}\\] \\[client %{IP:client_ip}\\] %{GREEDYDATA:error_message}: %{GREEDYDATA:file_path}"
    grok = Grok(grok_pattern)
    grok_match = grok.match(log_line)
    print(grok_match)


if __name__ == "__main__":
    verify_grok()
