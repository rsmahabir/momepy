#!/usr/bin/env python
# -*- coding: utf-8 -*-

# intensity.py
# definitons of intensity characters

from tqdm import tqdm  # progress bar
import geopandas as gpd


def radius(gpd_df, cpt, radius):
    """
    Get a list of indices of objects within radius.

    Parameters
    ----------
    gpd_df : GeoDataFrame
        GeoDataFrame containing point objects to analyse
    cpt : shapely.Point
        shapely point representing the center of radius
    radius : float
        radius

    Returns
    -------
    list
        Return only the neighbour indices, sorted by distance in ascending order

    Notes
    ---------
    https://stackoverflow.com/questions/44622233/rtree-count-points-in-the-neighbourhoods-within-each-point-of-another-set-of-po

    """
    # Spatial index
    sindex = gpd_df.sindex
    # Bounding box of rtree search (West, South, East, North)
    bbox = (cpt.x - radius, cpt.y - radius, cpt.x + radius, cpt.y + radius)
    # Potential neighbours
    good = []
    for n in sindex.intersection(bbox):
        dist = cpt.distance(gpd_df['geometry'][n])
        if dist < radius:
            good.append((dist, n))
    # Sort list in ascending order by `dist`, then `n`
    good.sort()
    # Return only the neighbour indices, sorted by distance in ascending order
    return [x[1] for x in good]


def frequency(objects, look_for, column_name, id_column='uID'):
    """
    Calculate frequency (count) of objects in a given radius.

    .. math::
        count

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    look_for : GeoDataFrame
        GeoDataFrame with measured objects (could be the same as objects)
    column_name : str
        name of the column to save the values
    id_column : str
        name of the column with unique id

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.

    References
    ---------

    """

    # define new column

    print('Calculating frequency...')

    objects_centroids = objects.copy()
    objects_centroids['geometry'] = objects_centroids.centroid

    look_for_centroids = look_for.copy()
    look_for_centroids['geometry'] = look_for_centroids.centroid

    objects_centroids[column_name] = None
    objects_centroids[column_name] = objects_centroids[column_name].astype('float')

    for index, row in tqdm(objects_centroids.iterrows(), total=objects_centroids.shape[0]):
        neighbours = radius(look_for_centroids, row['geometry'], 400)
        objects.loc[index, column_name] = len(neighbours)

    print('Frequency calculated.')
    return objects


def covered_area_ratio(objects, look_for, column_name, area_column, look_for_area_column, id_column="uID"):
    """
    Calculate covered area ratio of objects.

    .. math::
        \\textit{covering object area} \over \\textit{covered object area}

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects being covered (e.g. land unit)
    look_for : GeoDataFrame
        GeoDataFrame with covering objects (e.g. building)
    column_name : str
        name of the column to save the values
    area_column : str
        name of the column of objects gdf where is stored area value
    look_for_area_column : str
        name of the column of look_for gdf where is stored area value
    id_column : str
        name of the column with unique id. If there is none, it could be generated by unique_id().

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.

    References
    ---------

    """
    print('Calculating covered area ratio...')

    print('Merging DataFrames...')
    look_for = look_for[[id_column, look_for_area_column]]  # keeping only necessary columns
    objects_merged = objects.merge(look_for, on='uID')  # merging dataframes together

    print('Calculating CAR...')

    # define new column
    objects_merged[column_name] = None
    objects_merged[column_name] = objects_merged[column_name].astype('float')

    # fill new column with the value of area, iterating over rows one by one
    for index, row in tqdm(objects_merged.iterrows(), total=objects_merged.shape[0]):
            objects_merged.loc[index, column_name] = row[look_for_area_column] / row[area_column]

    # transfer data from merged df to original df
    print('Merging data...')
    objects[column_name] = objects_merged[column_name]

    print('Covered area ratio calculated.')
    return objects


def floor_area_ratio(objects, look_for, column_name, area_column, look_for_area_column, id_column="uID"):
    """
    Calculate floor area ratio of objects.

    .. math::
        \\textit{covering object floor area} \over \\textit{covered object area}

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects being covered (e.g. land unit)
    look_for : GeoDataFrame
        GeoDataFrame with covering objects (e.g. building)
    column_name : str
        name of the column to save the values
    area_column : str
        name of the column of objects gdf where is stored area value
    look_for_area_column : str
        name of the column of look_for gdf where is stored floor area value
    id_column : str
        name of the column with unique id. If there is none, it could be generated by unique_id().

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.

    References
    ---------

    """
    print('Calculating floor area ratio...')

    print('Merging DataFrames...')
    look_for = look_for[[id_column, look_for_area_column]]  # keeping only necessary columns
    objects_merged = objects.merge(look_for, on='uID')  # merging dataframes together

    print('Calculating FAR...')

    # define new column
    objects_merged[column_name] = None
    objects_merged[column_name] = objects_merged[column_name].astype('float')

    # fill new column with the value of area, iterating over rows one by one
    for index, row in tqdm(objects_merged.iterrows(), total=objects_merged.shape[0]):
            objects_merged.loc[index, column_name] = row[look_for_area_column] / row[area_column]

    # transfer data from merged df to original df
    print('Merging data...')
    objects[column_name] = objects_merged[column_name]

    print('Floor area ratio calculated.')
    return objects


def block_density(objects, column_name, blocks, block_id, unique_id):
    """
    Calculate the density of tessellation cells in a block.

    .. math::
        \\frac{\\sum_{i \\in block} (n_i)}{area_{block}} * 10 000

    Multiplication by 10 000 is converting value to units per hectare.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    blocks : GeoDataFrame
        GeoDataFrame containing blocks
    block_id : str
        name of the column with block id. If there is none, it could be generated by unique_id()
    unique_id : str
        name of the column with unique id. If there is none, it could be generated by unique_id()

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.

    References
    ---------
    Feliciotti A (2018) RESILIENCE AND URBAN DESIGN:A SYSTEMS APPROACH TO THE
    STUDY OF RESILIENCE IN URBAN FORM. LEARNING FROM THE CASE OF GORBALS. Glasgow.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating block density...')

    block_ids = objects[block_id].tolist()

    unique_block_ids = list(set(block_ids))

    cells = {}
    areas = {}

    for id in unique_block_ids:
        unique_IDs = len(set(objects.loc[objects[block_id] == id][unique_id].tolist()))
        cells[id] = unique_IDs
        areas[id] = blocks.loc[blocks[block_id] == id].iloc[0]['geometry'].area

    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        objects.loc[index, column_name] = 10000 * cells[row[block_id]] / areas[row[block_id]]

    print('Block density calculated.')
    return objects
# objects.to_file("/Users/martin/Strathcloud/Personal Folders/Test data/Prague/p7_voro_single4.shp")
#
# objects = gpd.read_file("/Users/martin/Strathcloud/Personal Folders/Test data/Prague/p7_voro_single.shp")
# column_name = 'test'
# objects
# objects2.head
# objects['geometry'] = objects.centroid
# objects_centroids
