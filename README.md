Organizer of Copernicus Sentinel Science Hub downloader KMLs files
==================================================================

This simple plugin can be used to organize in a hierarchy of groups
within the Layout Tree the KMLs files generated by 'scihub' program,
tool available at https://github.com/fpl/scihub

The hierarchy used is:

       Satellite
       |
       +---> Product
            |
            +---> Orbit direction
                  |
                  +---> Relative Orbit #
                        |
                        +---> Year
                              |
                              +---> Month
                                    |
                                    +---> KML layer


Each layer keep the full ESA file name and is added to
the right <month> on the basis of the extended data available
in the KML file.

