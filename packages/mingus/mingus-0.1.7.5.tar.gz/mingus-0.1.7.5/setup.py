from distutils.core import setup

setup(name= "mingus",
	  version = "0.1.7.5",
	  description = "Music theory and notation package",
	  author = "Bart Spaans",
	  author_email = "onderstekop@gmail.com",
	  url = "http://mingus.googlecode.com/",
	  packages = ['mingus', 'mingus.core', 'mingus.containers', 'mingus.draw'],
	  package_data = {'mingus.draw': ['data/*.png', 'data/*.gif']}
	  )
