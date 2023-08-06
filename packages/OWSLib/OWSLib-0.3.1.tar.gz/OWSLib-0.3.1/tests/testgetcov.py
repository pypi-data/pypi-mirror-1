from owslib.wcs import WebCoverageService
wcs=WebCoverageService('http://localhost:5000/famous_control_month/wcs', version='1.0.0')
output=wcs.getCoverage(identifier='FC7TrL3o',time=['2793-04-16T00:00:00.0'],bbox=(-80,30,50,60), format='cf-netcdf')