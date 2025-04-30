<div align="center">

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/banner.png" alt="OSRS Economy Banner" style="width: 100%; padding-bottom: 10px;"/>

<br>

<p>An <strong>ELT pipeline</strong> to monitor the economy of <em>Old School RuneScape</em>.</p>

</div>

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/divider.png" alt="Custom Divider Image" style="width: 100%;"/>

- [Introduction](#introduction)
- [Data Sources](#data-sources)
- [Architecture](#architecture)
- [Improvements](#improvements)
- [Acknowledgements](#acknowledgements)
- [Authors](#authors)

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/divider.png" alt="Custom Divider Image" style="width: 100%;"/>

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

Data was extracted from the sources listed in the [Data Sources](#data-sources) section. To do this, a supporting Python library (located in the `src` directory) was created to extract data from the various sources. This library handles making requests to the various APIs, performing the bare minimum amount of data wrangling to get the data into the desired format for loading, and interacting with the appropriate cloud services.

The extraction and loading processes were orchestrated using an Airflow and containerized using Docker. The Airflow DAG runs 12 times per day; this seemed like a reasonable number of runs in order to get some variance in price data, and to ensure that an interesting amount of data was being ingested.

### Load

The extracted data was loaded into Cloud Storage buckets for archival purposes, and into BigQuery tables for downstream processing and analysis.

See below for an ER diagram of the BigQuery database.

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/er-diagram.png" alt="OSRS Economy ELT ER Diagram" style="width: 100%;"/>

The database follows a [medallion architecture](https://www.databricks.com/glossary/medallion-architecture), which is a design pattern that allows for the separation of concerns between the data layer and the application layer.

Typically, the bronze layer is where raw data is loaded, the silver layer is for cleaned and transformed data, and the gold layer is aggregated data that is used for the final analysis and visualization.

The extracted data was already quite clean, thus the silver layer was omitted so as to not overcomplicate the project (more than has already been done).

> [!NOTE]
> Please keep in mind that the intention of this project is not to have a sprawling, massive database, but rather to have a relatively simple database that provides a foundation to use more advanced tools.

### Transform

Transformations were applied to the data and the gold layer of the database was creating using jobs on dbt Cloud. The transformations were primarily focused on reducing the amount of queries and filters necessary for visualization by providing the data directly.

### Visualize

A [report](https://tinyurl.com/osrs-economy) was created to visualize the data. It is fairly barebones, since creating a beautiful report is not the goal of this project; it is simply a way to show that the data exists and is able to be visualized and analyzed. That said, I may improve this report in the future.

## Improvements

A project is never truly _done_ since someone who cares about their work will always see little things that could have been done differently. In my case, I got the output I initially wanted, so I simply wanted to move onto my next project.

If I had to start this project from scratch or rework it in the future, I would take the following lessons and potential improvements into account:

- Simplify the data extraction process.
  - The _WeirdGloop_ API is currently being used to fetch item prices, but the _Wiki_ API could be used for this purpose on top of its existing functionality.
  - This would improve complexity by decreasing the number of APIs being used from 3 to 2.
- Rework the `src` directory.
  - Since Airflow was added into the project late in development, the extract and load processes were originally envisioned as a command-line tool; the remnants of this can be seen in `main.py`.
  - I'm not sure exactly what I would have preferred to do instead, but this part of the architecture feels like it doesn't flow smoothly with Airflow. - Honestly, even if this is a good example of how a project can be over-engineered, it helps me exercise my general software engineering design skills, so I'm not super worried about changing this.
- Utilize Airflow DAGs more effectively.
  - Initially, Airflow was not going to be used for this project, so its addition was done relatively haphazardly.
  - Currently, only a single DAG is being used to ingest the data, but this process could be split into multiple DAGs to improve the robustness and transparency of the process.
  - This would also allow for extracted data to be stored in Cloud Storage and BigQuery in parallel instead of sequentially.
  - I have no regrets adding it to the project, but since its inclusion was born from feature creep, the execution could definitely be improved.
- Add an autoincrementing primary key to the prices tables.
  - I meant to do this in the first place, but then I forgot. Then, suddenly, I was in too deep and it turns out I didn't have an urgent need for it anyways.
- Use tables instead of views for the gold layer.
  - Currently, the gold layer entities created using dbt are views, but these are traditionally tables.
  - The only reason I chose to use views was because I wanted to avoid extraneous storage costs, but after working with the project for a while, it became obvious that storage costs were not a concern anyways.

<img src="https://raw.githubusercontent.com/jakebrehm/osrs-economy/master/img/divider.png" alt="Custom Divider Image" style="width: 100%;"/>

## Acknowledgements

This project was possible thanks to the teams at the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/) and [WeirdGloop](https://weirdgloop.org/) for their generosity in providing public access to their data and APIs, as well as the overall Old School RuneScape community for playing the game so that I had data to work with. 😎

## Authors

- **Jake Brehm** - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)
