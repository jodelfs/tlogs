import pandas as pd

max_nr_logs = 40
max_nr_pnts = 20

log_qualities = [-1, 0, 1, 2, 3]

# for temperature interpolation
depth_list = list(range(0, 1000, 10))
#depth_list += list(range(300, 1000, 50))

debug_note_length = 40
# results
selected_sample_initial = '0' # must be str
surface_temperature_initial = pd.NA
depth_bottom_initial =  pd.NA
depth_top_initial = pd.NA
quality_initial = -1
note_initial = ''
water_level_initial = pd.NA
static_water_level_initial = pd.NA
date_initial = pd.NA

elevation_initial = pd.NA
#sealing_initial = pd.NA
#vegetation_initial = pd.NA
#land_use_initial = ''
#land_cover_initial = ''
#tree_cover_initial = pd.NA

#slope_initial = pd.NA
#aspect_initial = pd.NA

#Nxxx_initial = pd.NA

land_use_dict = {
    'N112': 'Wohnen',
    'N120': 'Produktion',
    'N121': 'Öffentlichkeit',
    'N122': 'Straßen- und Bahnverkehr',
    'N123': 'Hafen',
    'N124': 'Flugverkehr',
    'N131': 'Abbauflächen',
    'N132': 'Deponien',
    'N133': 'Baustelle',
    'N141': 'Städtische Grünfläche',
    'N142': 'Sport und Freizeit',
    'N211': 'Landwirtschaftliche Fläche',
    'N214': 'Extensive landwirtschaftliche Nutzung',
    'N311': 'Forst',
    'N510': 'Wasser',
    'N999': 'Nicht relevant'
}


land_cover_dict = {
    'N112': {'B110': 'Wohnbebauung',
             'B122': 'Fussgängerzone',
             'B231': 'Lockere vegetationsdominierte Bebauung',
             'B233': 'Lockere vegetationsdominierte Bebauung',
             'B310': 'Lockere vegetationsdominierte Bebauung',
             'B311': 'Lockere vegetationsdominierte Bebauung',
             'B312': 'Lockere vegetationsdominierte Bebauung',
             'B313': 'Lockere vegetationsdominierte Bebauung',
             'B330': 'lockere Bebauung, Dominanz von Schotter, bzw unversiegelter Boden',
             'B242': 'Bungalowsiedlung, regelmäßige Struktur'

             },
    'N120': 'Produktion',
    'N121': 'Öffentlichkeit',
    'N122': {'B122': 'Autobahn, Parkplatz',
             'B310': 'Kleeblatt',
             'B311': 'Kleeblatt',
             'B312': 'Kleeblatt',
             'B313': 'Kleeblatt',
             'B321': 'Kleeblatt',
             'B322': 'Kleeblatt',
             'B324': 'Kleeblatt',
             'B332': 'Kleeblatt',
             'B231': 'Kleeblatt',
             'B233': 'Kleeblatt',
             'B110': 'Raststättem, Bahnhofsgebäude',
             'B330': 'Eisenbahn',
             'B3': 'Kleeblatt',
             },
    'N123': 'Hafen',
    'N124':  {'B122': 'Landebahnen, Parkplatz',
              'B310': 'Grünflächen',
              'B311': 'Grünflächen',
              'B312': 'Grünflächen',
              'B313': 'Grünflächen',
              'B321': 'Grünflächen',
              'B322': 'Grünflächen',
              'B324': 'Grünflächen',
              'B330': 'Grünflächen',
              'B332': 'Grünflächen',
              'B231': 'Grünflächen',
              'B233': 'Grünflächen',
             ' B110': 'Gebäude',
             'B121': 'Besondere Infrastrukturanlagen',
             },
    'N131': 'Abbauflächen',
    'N132': 'Deponien',
    'N133': {'B330': 'Bauaktivität',
             'B310': 'bei existierenden neuen Wegenetzen',
             'B311': 'bei existierenden neuen Wegenetzen',
             'B312': 'bei existierenden neuen Wegenetzen',
             'B313': 'bei existierenden neuen Wegenetzen',
             'B321': 'bei existierenden neuen Wegenetzen',
             'B322': 'bei existierenden neuen Wegenetzen',
             'B324': 'bei existierenden neuen Wegenetzen',
             'B330': 'bei existierenden neuen Wegenetzen',
             'B332': 'bei existierenden neuen Wegenetzen',
             'B231': 'bei existierenden neuen Wegenetzen',
             'B233': 'bei existierenden neuen Wegenetzen',
             'B110': 'Keine Nutzung erkennbae',
             'B121': 'Keine Nutzung erkennbar'
             },
    'N141': {'B242': 'Friedhof',
             'B310': 'Park, Hundewiese',
             'B311': 'Park, Hundewiese',
             'B312': 'Park, Hundewiese',
             'B313': 'Park, Hundewiese',
             'B321': 'Park, Hundewiese',
             'B322': 'Park, Hundewiese',
             'B324': 'Park, Hundewiese',
             'B330': 'Park, Hundewiese',
             'B332': 'Park, Hundewiese',
             'B231': 'Park, Hundewiese',
             'B233': 'Park, Hundewiese'
             },
    'N142': {'B110': 'Kloster',
             'B122': 'Parkpätze in Anlage',
             'B310': 'Park, Boots-, Flughafen',
             'B311': 'Park, Boots-, Flughafen',
             'B312': 'Park, Boots-, Flughafen',
             'B313': 'Park, Boots-, Flughafen',
             'B321': 'Park, Boots-, Flughafen',
             'B322': 'Park, Boots-, Flughafen',
             'B324': 'Park, Boots-, Flughafen',
             'B330': 'Park, Boots-, Flughafen',
             'B332': 'Park, Boots-, Flughafen',
             'B231': 'Hundewiese',
             'B233': 'Park, Boots-, Flughafen',
             'B121': 'Sporthalle, Hallenbad',
             'B242': 'Schrebergarten unabhängig von Ortslage, Friedhof ausserhalb Stadt'
             },
    'N211': 'Landwirtschaftliche Fläche',
    'N214': 'Extensive landwirtschaftliche Nutzung',
    'N311': 'Forst',
    'N510': 'Wasser',
    'N999':  {
             'B310': 'Grünstreigen an Verkehrsfächen, Flüssen',
             'B311': 'Kleine Waldflächen',
             'B312': 'Kleine Waldflächen',
             'B313': 'Kleine Waldflächen',
             'B321': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B322': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B324': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B330': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B332': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B231': 'Grünstreifen an Verkehrsflächen, Flüssen',
             'B233': 'Grünstreifen an Verkehrsflächen, Flüssen',
             },
}
