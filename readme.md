<div align="center">

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/banner.png" alt="OSRS Economy Banner" style="width: 100%; padding-bottom: 10px;"/>

<br>

<p>An <strong>ELT pipeline</strong> to monitor the economy of <em>Old School RuneScape</em>.</p>

</div>

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/divider.png" alt="Divider" style="width: 100%; padding-top: 20px; padding-bottom: 20px;"/>

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/table-of-contents.png" alt="Table of Contents Section" style="width: 100%;"/>

- [Introduction](#introduction)
- [Data Sources](#data-sources)
- [Architecture](#architecture)
- [Improvements](#improvements)
- [Acknowledgements](#acknowledgements)
- [Authors](#authors)

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/project-overview.png" alt="Project Overview Section" style="width: 100%;"/>

## Introduction

This project aims to monitor the economy of [Old School RuneScape](https://oldschool.runescape.com/) by employing an ELT pipeline to extract data from various APIs and load it into a database for analysis and visualization.

It is **completely, but intentionally, over-engineered**. The final product could have been achieved with a much simpler tech stack, but the goal of and motivation for this project was to further develop skills with industry-standard tools and incorporate them into a simple, yet powerful project.

## Data Sources

The following data sources are used in this project:

| Name                                                                       | Description                                         |
| -------------------------------------------------------------------------- | --------------------------------------------------- |
| [OSRS Wiki](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices) | Used to get a list of item IDs.                     |
| Item Details                                                               | Undocumented API used to get details for each item. |
| [WeirdGloop](https://api.weirdgloop.org/)                                  | The API used to fetch item prices.                  |

## Architecture

Please refer to the architecture diagram below for a visual representation of the project's architecture.

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/architecture-diagram.png" alt="OSRS Economy ELT Architecture Diagram" style="width: 100%;"/>

### Summary

1. Provision [Google Cloud Platform](https://cloud.google.com/) resources using [Terraform](https://www.terraform.io/).
2. Extract data from REST APIs using [Python](https://www.python.org/).
3. Load data into [Cloud Storage](https://cloud.google.com/storage) buckets and [BigQuery](https://cloud.google.com/bigquery) tables.
4. Orchestrate the extract and load processes using [Airflow](https://airflow.apache.org/).
5. Containerize the application using [Docker](https://www.docker.com/).
6. Apply transformations to the data using [dbt](https://www.getdbt.com/).
7. Visualize the data in a report using [Google Data Studio](https://lookerstudio.google.com/).

### Extract

Data was extracted from the sources listed in [Data Sources](#data-sources). To do this, a supporting Python library (located in the [`src`](/src/) directory) was created to extract data from the various sources, and the library served as the backend for a command-line tool and Airflow DAGs.

The extraction and loading processes were orchestrated using an Airflow and containerized using Docker.

- The Airflow DAG to ingest item details runs _hourly_, mostly because it only fully runs if an item is missing or if current details are outdated (the threshold for which is an adjustable setting).
- The DAG to ingest price data runs _12 times per day_; this seemed like a reasonable frequency to get some variance in price data and to ensure that an interesting amount of data was being ingested.

### Load

The extracted data was loaded into Cloud Storage buckets for archival purposes, and into BigQuery tables for downstream processing and analysis.

See below for an ER diagram of the BigQuery database.

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/er-diagram.png" alt="OSRS Economy ELT ER Diagram" style="width: 100%;"/>

The database follows a [medallion architecture](https://www.databricks.com/glossary/medallion-architecture) design pattern.

Typically, the bronze layer is where raw data is loaded, the silver layer is for cleaned and transformed data, and the gold layer is for analysis- and reporting-ready data. However, the extracted data was already quite clean, thus the silver layer was omitted so as to not further overcomplicate the project.

> [!NOTE]
> Please keep in mind that the intention of this project is not to have a sprawling, massive database, but rather to have a relatively simple database that provides a foundation to use more advanced tools.

### Transform

Transformations were applied to the data and the gold layer of the database was creating using jobs on dbt Cloud. The transformations were primarily focused on reducing the amount of queries and filters necessary for visualization by providing the data directly.

### Visualize

A [report](https://tinyurl.com/osrs-economy) was created to visualize the data. A screenshot is included below in case I decide to stop supporting the project.

It is fairly barebones, since creating a beautiful report was not the primary goal of this project; it is simply a way to show that the data exists.

<div align="center">

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/report.png" alt="Report Screenshot" style="width: 100%;"/>

</div>

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/divider.png" alt="Divider" style="width: 100%; padding-top: 20px; padding-bottom: 20px;"/>

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/closing-thoughts.png" alt="Closing Thoughts Section" style="width: 100%;"/>

## Improvements

A project is never truly _done_ since someone who cares about their work will always see little things that could have been done differently. In my case, I got the output I initially wanted, so I simply wanted to move onto my next project.

If I had to start this project from scratch or rework it in the future, I would take the following lessons and potential improvements into account:

- **Use different APIs**.
  - Since starting this project, the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices) has added API endpoints (or I just wasn't aware of them).
  - The [`/mapping`](https://prices.runescape.wiki/api/v1/osrs/mapping) endpoint completely invalidates the way I gathered item details using my [`details`](/airflow/dags/details_pipeline.py) DAG.
  - The [`/5m`](https://prices.runescape.wiki/api/v1/osrs/5m) endpoint provides nearly real-time price data, including average high and low prices.
- **Rework the [`src`](/src/) directory**.
  - Before deciding to add Airflow late in development, the project was a command-line tool.
    - The remnants of this can be seen in [`main.py`](main.py) and in the Airflow DAGs.
  - I would refactor the source code to be more suited for Airflow.
  - This is a good example of over-engineering, but it did help me exercise my general software engineering skills.
- **Utilize Airflow DAGs more effectively**.
  - Currently, there are only two DAGs: one to ingest item details and another to ingest prices.
  - These DAGs could each be split into multiple DAGs to improve robustness and transparency.
  - Extracted data could be stored in Cloud Storage and BigQuery in parallel instead of sequentially.
- **Use tables instead of views for the gold layer**.
  - Currently, the gold layer entities created using dbt are views, but these would traditionally be tables.
  - I chose to use views to avoid extraneous storage costs, but with time it became clear this wasn't a concern.

## Acknowledgements

This project was possible thanks to the teams at the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/) and [WeirdGloop](https://weirdgloop.org/) for their generosity in providing public access to their data and APIs, as well as the overall Old School RuneScape community for playing the game so that I had data to work with. 😎

## Authors

- **Jake Brehm** - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)
