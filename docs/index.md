<p align="center">
  <img src="http://logos.u2d.ai/msaBase_logo.png?raw=true" alt="MSA Base image"/>
</p>

------
<p align="center">
    <em>msaBase- Main package based on FastAPI like Profiler, Scheduler, Sysinfo, Healtcheck, Error Handling etc.</em>
<br>
  <a href="https://pypi.org/project/msaBase" target="_blank">
      <img src="https://img.shields.io/pypi/v/msaBase?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypi.org/project/msaBase" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/msaBase.svg?color=%2334D058" alt="Supported Python versions">
  </a>
</p>

------


### Usage example
```python
{!./docs_src/home/index_first.py!}
```

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
