import os

modules = "grid.base.js; jquery.fmatter.js; grid.custom.js; grid.common.js; grid.formedit.js; jquery.searchFilter.js; grid.inlinedit.js; grid.celledit.js; jqModal.js; jqDnR.js; grid.subgrid.js; grid.treegrid.js; grid.import.js; JsonXml.js; grid.setcolumns.js; grid.postext.js; grid.tbltogrid.js; grid.jqueryui.js;"
modules = [module.strip() for module in modules.split(";") if module.strip()]

os.system('cat %s > out.js' % (' '.join(modules)))



