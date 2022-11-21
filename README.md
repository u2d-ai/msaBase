<p align="center">
  <img src="http://logos.u2d.ai/msaBase_logo.png?raw=true" alt="msaBase
</p>

------
<p align="center">
    <em>msaBase- General Package for Microservices based on FastAPI like Profiler, Scheduler, Sysinfo, Healtcheck, Error Handling etc.</em>
<br>
    Optimized for use with FastAPI/Pydantic.
<br>
  <a href="https://pypi.org/project/msaBase" target="_blank">
      <img src="https://img.shields.io/pypi/v/msaBase?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypi.org/project/msaBase" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/msaBase.svg?color=%2334D058" alt="Supported Python versions">
  </a>
</p>

------

**Documentation**: <a href="https://msaBase.u2d.ai/" target="_blank">Documentation (https://msaBase.u2d.ai/)</a>

------

## Features
- **MSABaseExceptionHandler**: Central exception handler which sends formatted exception to logger
- **Filehandler utilities**: Classes for FileDelete, FileUpload async with chunking, Archive pack/unpack formats, helper functions
- **mkdocs code reference helper**: Create virtual mkdocs navs for code reference and used libraries from requirements.txt
- **MSAHealthCheck**: Healthcheck class with internal own thread, which checks url for health
- **logger intercept handler**: allows to change handler from all logger and define specific output format with loguru
- **Models for files and health classes**: reusable pydantic models for file handling and dealing with healthcheck status
- **MSAProfilerMiddleware**: PyInstrument Profiler as Middleware to create a html for an admin Dashboard
- **MSAAppSettings**: API oriented settings class with environment vars and `.env` file support
- **Service oriented System Info**: Classes and functions to get pydantic model response about system and gpu information

## License Agreement

- `msaBase`Based on `MIT` open source and free to use, it is free for commercial use, but please show/list the copyright information about msaBase somewhere.


## How to create the documentation

We use mkdocs and mkdocsstring. The code reference and nav entry get's created virtually by the triggered python script /docs/gen_ref_pages.py while ``mkdocs`` ``serve`` or ``build`` is executed.

### Requirements Install for the PDF creation option:
PDF Export is using mainly weasyprint, if you get some errors here pls. check there documentation. Installation is part of the msaBase, so this should be fine.

We can now test and view our documentation using:

    mkdocs serve

Build static Site:

    mkdocs build


## Build and Publish
  
Build:  

    python setup.py sdist

Publish to pypi:

    twine upload dist/*
