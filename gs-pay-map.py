
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import QName

from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, WheelZoomTool, PanTool, SaveTool, HoverTool
from bokeh.tile_providers import Vendors, get_provider
from boken.resources import CDN
from bokeh.palettes import brewer
from bokeh.layouts import columns
from bokeh.emded import file_html, components

import cenpy

import requests

def is_xml_present():
  return False

def fetch_xml():
  with requests.get("https://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages/2024/general-schedule") as req:
    bs = BeautifulSoup(req.text)
    # https://beautiful-soup-4.readthedocs.io/en/latest/#installing-beautiful-soup
    pass

def read_xml():
  pass

def fetch_counties():
  with requests.get("https://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages/2024/locality-pay-area-definitions/") as req:
    bs = BeautifulSoup(req.text)
    cols = bs.find_all("h3")
    # TODO: skip the first few, maybe just h3 that have anchor tags with ids for deep links?
    for col in cols:
      # TODO: get the table from each h3 section, with has counties (ignore) and FIPS id (yes)
      pass

def county_maps(counties):
  pass

def make_map(gs_data, county_map_data):
  # TODO: map gs_data and county_map_data to geo_loc_counts, and geosource
  # bokeh docs: https://docs.bokeh.org/en/latest/index.html
  zoom_tool = WheelZoomTool(zoom_on_axis=False)
  tools = [PanTool(), zoom_tool, SaveTool()]
  # TODO: tooltips?
  map_plot = figure(title="GS Locations", x_axis_type="mercator", y_axis_type="mercator", tools=tools)
  map_plot.sizing_mode = "stretch_width"
  map_plot.toolbar.active_scroll = zoom_tool

  # https://docs.bokeh.org/en/latest/docs/reference/tile_providers.html#bokeh-tile-providers
  map_plot.add_tile(get_provider(Vendors.CARTODBPOSITRON))

  # Settled on brewer for colors: https://colorbrewer2.org
  # Was considering `colorcet`, but https://arxiv.org/pdf/1509.03700v1.pdf says stick with brewer
  palette = list(reversed(brewer['YlGnBu'][5]))  # Gets yellow as low and blue as high
  vals = geo_loc_counts["pay_amount"]
  if vals.empty:
    max_val = 100_000
  else:
    max_val = max(vals)

  color_mapper = LinearColorMapper(palette=palette, low=0, high=max_val)
  map_plot.patches('xs', 'ys', source=geosource,
                     fill_color={'field': 'pay_amount', 'transform': color_mapper},
                     line_color='black', line_width=0.5, fill_alpha=0.5)
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, height=20,
                         border_line_color=None, location=(0, 0),
                         orientation='horizontal')
  map_plot.add_layout(color_bar, 'below')
  return map_plot

def main():
  if not is_xml_present():
    fetch_xml()
  gs_data = read_xml()
  counties = fetch_counties()

  county_map_data = county_maps(counties)

  make_map(gs_data, county_map_data)
