# Stolen from http://www.djangosnippets.org/snippets/1049/
import urllib, codecs

COUNTRY_INFO_URL = "http://download.geonames.org/export/dump/countryInfo.txt"

def get_geonames_country_data():
    "Returns a list of dictionaries, each representing a country"
    udata = urllib.urlopen(COUNTRY_INFO_URL).read().decode('utf8')
    # Strip the BOM
    if udata[0] == codecs.BOM_UTF8.decode('utf8'):
        udata = udata[1:]
    # Ignore blank lines
    lines = [l for l in udata.split('\n') if l]
    # Find the line with the headers (starts #ISO)
    header_line = [l for l in lines if l.startswith('#ISO')][0]
    headers = header_line[1:].split('\t')
    # Now get all the countries
    country_lines = [l for l in lines if not l.startswith('#')]
    countries = []
    for line in country_lines:
        countries.append(dict(zip(headers, line.split('\t'))))
    return countries

if __name__ == "__main__":
    country_metadata = dict([(c["Country"], c)
                                for c in get_geonames_country_data()])
    countries_sorted = sorted(country_metadata.keys())
    iso_name_choices = [(str(country_metadata[country]["ISO"].lower()),
                       country) for country in countries_sorted]
    iso_names = dict(iso_name_choices)
    print("iso_names = %s" % iso_names)
    print("iso_name_choices = %s" % iso_name_choices)

