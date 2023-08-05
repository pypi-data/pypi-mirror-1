from setuptools import setup, find_packages

setup(
      name = "treemap",
      author = "James Casbon",
      version = "1.05", 
      package_dir = {'':'src'},
      packages = find_packages("src"),
      #install_requires = ['matplotlib'],
      author_email = "casbon@gmail.com",
      description = "Treemap creator with interactive viewer",
      long_description = """This module gives you an easy way to create a treemap
      from pretty much any data.  You can read about the history of treeviews 
      at http://www.cs.umd.edu/hcil/treemap-history/index.shtml.  This 
      implementation uses pylab to display the resulting map, and the map can
      be zoomed by clicking on a node. """,
      url = "http://www.machine-envy.com/blog/?p=47",
      entry_points = {
        'gui_scripts': [
            'treemap_demo = treemap.scripts:example',
            'treemap_coverage = treemap.scripts:test_coverage',
        ]
    }
      
)
