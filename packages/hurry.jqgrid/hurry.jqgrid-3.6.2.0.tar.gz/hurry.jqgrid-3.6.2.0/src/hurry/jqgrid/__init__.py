from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery
from hurry.jqueryui import jqueryui

jqgrid_library = Library('jqgrid')

# css
grid_css = ResourceInclusion(
    jqgrid_library, 'src/css/ui.jqgrid.css')

# base
grid_base = ResourceInclusion(
    jqgrid_library, 'src/grid.base.js',
    depends=[jquery, grid_css])

jquery_fmatter = ResourceInclusion(
    jqgrid_library, 'src/jquery.fmatter.js',
    depends=[jquery])
grid_custom = ResourceInclusion(
    jqgrid_library, 'src/grid.custom.js',
    depends=[grid_base])

# editing
grid_common = ResourceInclusion(
    jqgrid_library, 'src/grid.common.js',
    depends=[grid_base])
jquery_searchfilter_css = ResourceInclusion(
    jqgrid_library, 'src/css/jquery.searchfilter.css')
jquery_searchfilter = ResourceInclusion(
    jqgrid_library,'src/jquery.searchfilter.js',
    depends=[jquery, jquery_searchfilter_css])
grid_formedit = ResourceInclusion(
    jqgrid_library, 'src/grid.formedit.js',
    depends=[grid_common, jquery_searchfilter])
grid_inlinedit = ResourceInclusion(
    jqgrid_library, 'src/grid.inlinedit.js',
    depends=[grid_common])
grid_celledit = ResourceInclusion(
    jqgrid_library, 'src/grid.celledit.js',
    depends=[grid_base])
jqmodal = ResourceInclusion(
    jqgrid_library, 'src/jqModal.js',
    depends=[jquery])

# subgrid
grid_subgrid = ResourceInclusion(
    jqgrid_library, 'src/grid.subgrid.js',
    depends=[grid_base])

# treegrid
grid_treegrid = ResourceInclusion(
    jqgrid_library, 'src/grid.treegrid.js',
    depends=[grid_base])

# import/export
jsonxml = ResourceInclusion(
    jqgrid_library, 'src/JsonXml.js')
grid_import = ResourceInclusion(
    jqgrid_library, 'src/grid.import.js',
    depends=[grid_base])

# other modules
grid_setcolumns = ResourceInclusion(
    jqgrid_library, 'src/grid.setcolumns.js',
    depends=[grid_base])

grid_postext = ResourceInclusion(
    jqgrid_library, 'src/grid.postext.js',
    depends=[grid_base])

grid_tbltogrid = ResourceInclusion(
    jqgrid_library, 'src/grid.tbltogrid.js',
    depends=[grid_base])

# jQuery UI addon methods
grid_jqueryui = ResourceInclusion(
    jqgrid_library, 'src/grid.jqueryui.js',
    depends=[grid_base, jqueryui])

# multiselect
ui_multiselect_css = ResourceInclusion(
    jqgrid_library,
    'src/css/ui.multiselect.css')
ui_multiselect = ResourceInclusion(
    jqgrid_library, 'src/ui.multiselect.js',
    depends=[jqueryui, ui_multiselect_css])

# locales
locale_en = ResourceInclusion(
    jqgrid_library, 'src/i18n/grid.locale-en.js',
    depends=[jquery])
