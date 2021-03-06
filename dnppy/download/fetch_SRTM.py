__author__ = 'jwely'

from dnppy import core
from download_url import download_url
import os
import zipfile


def fetch_SRTM(ll_lat, ll_lon, ur_lat, ur_lon, product, outdir = None, mosaic = None):
    """
    downloads data from the Shuttle Radar Topography Mission (SRTM)
    [http://e4ftl01.cr.usgs.gov/SRTM/]

    This data can be used to create DEMs of a variety of resolutions.

    :param ll_lat:      latitude of lower left corner
    :param ll_lon:      longitude of lower left corner
    :param ur_lat:      latitude of upper right corner
    :param ur_lon:      longitude of upper right corner
    :param product:     short name of product you want. See http://e4ftl01.cr.usgs.gov/SRTM/ .
                        do not include the version number. Example: "SRTMGL1". Note
                        that version "002" data of .DEM format does not support mosaicing.
    :param outdir:      local directory to save downloaded files
    :param mosaic:      Set to TRUE to mosaic all downloaded DEM tiles as "SRTM_mosaic.tif"

    :return tile_list:   a list of all successfully downloaded tif filepaths
                        for further manipulation

    NOTE: arcmap will open the output hgt files ONLY if they are not renamed.
    turns out arcmap does some funky things when interpreting these files.
    """

    # build empty return list
    tile_list = []

    # build list of lat/lon pairs from input corners
    lat_lon_pairs = []
    for i in range(int(ll_lat), int(ur_lat + 1)):
        for j in range(int(ll_lon), int(ur_lon + 1)):
            lat_lon_pairs.append((i, j))

    print lat_lon_pairs

    # determine product version
    if product is "SRTMGL30":
        print("Download of product SRTMGL30 is supported, but arcmap does not support this filetype")
        format_string = "{2}{3}{0}{1}.{4}.dem.zip"
        version = "002"
        mosaic = None

    else:
        format_string = "{0}{1}{2}{3}.{4}.hgt.zip"
        version = "003"


    host = "http://e4ftl01.cr.usgs.gov/SRTM"
    subhost = "{0}/{1}.{2}/2000.02.11/".format(host, product, version)

    print("Connecting to host at {0}".format(subhost))


    for lat_lon_pair in lat_lon_pairs:
        lat, lon = lat_lon_pair

        # set North-south, East-West convention.
        if lat >= 0:
            NS = "N"
        else:
            NS = "S"

        if lon >= 0:
            EW = "E"
        else:
            EW = "W"

        if product is "SRTMGL30":

            if abs(lon) <= 20:
                lon = 20
            elif abs(lon) <=60:
                lon = 60
            elif abs(lon) <= 100:
                lon = 100
            else:
                lon = 140

            if abs(lat) <= 10:
                lat = 10
            elif abs(lat) <=40:
                lat = 40
            else:
                lat = 90

            NS = NS.lower()
            EW = EW.lower()

        # build up the filename and file link
        filename = format_string.format(NS, str(abs(lat)).zfill(2),
                                        EW, str(abs(lon)).zfill(3),
                                        product)

        filelink = "{0}/{1}".format(subhost, filename)

        # decide where to put the file, then download it
        if outdir is not None:
            outpath  = os.path.join(outdir, filename)
        else:
            outpath = filename

        print("Downloading and extracting  {0}".format(filename))
        download_url(filelink, outpath)

        # unzip the file and reassemble descriptive name
        with zipfile.ZipFile(outpath, "r") as z:

            if version == "003":
                itemname = "{0}{1}{2}{3}.hgt".format(NS, str(abs(lat)).zfill(2),
                                                    EW, str(abs(lon)).zfill(3))
            elif version =="002":
                itemname = "{0}{1}{2}{3}.DEM".format(EW.upper(), str(abs(lon)).zfill(3),
                                                     NS.upper(), str(abs(lat)).zfill(2))

            z.extract(itemname, outdir)
            z.close()

        # clean up and add this file to output list
        os.remove(outpath)
        tile_list.append(os.path.join(outdir,itemname))

    print("Finished download and extraction of SRTM data")

    if mosaic is True:

        # use gdal to mosaic these raster together
        out_mosaic  = os.path.join(outdir, "SRTM_mosaic.tif")
        core.run_command("gdalwarp", tile_list, out_mosaic)
        return out_mosaic

    else:
        return tile_list


if __name__ == "__main__":

    testdir = r"C:\Users\jwely\Desktop\troubleshooting\SRTM"
    fetch_SRTM(47, -118, 48, -118, "SRTMGL3", testdir, mosaic = True)


