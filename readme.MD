# Travel Planner API

## Overview

Travel Planner API is a Django REST Framework -based backend for
managing travel projects and places within them.

A **Travel Project** represents a trip or plan. Each project contains
**places**, identified by an external ID from the **Art Institute of
Chicago API**. For every place inside a project, the system stores
**project-specific data** such as notes and visited status.

The API is designed with clear separation of concerns: - Places are
global entities (by `external_id`) - Project--place relations are
handled via an intermediate model - Validation of external data happens
at the model level

## Core Concepts

### TravelProject

Represents a travel plan.

Key fields: - `name` - `description` - `start_date` - `is_completed`
(calculated automatically)

Rules: - A project must contain **at least one place** - A project
**cannot be deleted** if it has visited places - A project is marked as
completed when **all places are visited**

### ProjectPlace

Represents a place fetched from an external API.

Key fields: - `external_id` (unique, from Art Institute API) - `title`
(fetched automatically from the API)

Validation: - On creation, the API is queried to ensure the place
exists - If the external API does not return data, validation fails

### ProjectPlaceAssignment

Intermediate model between `TravelProject` and `ProjectPlace`.

Stores project-specific data: - `notes` - `visited`

This allows the same place to be reused across multiple projects with
different states.

## API Structure

### Projects

Base endpoint:

    /api/projects/

Supported operations: - Create a project with a list of `external_id`s -
Retrieve, update, and delete projects - Nested places are readable,
updates handled separately

### Places within a Project

    /api/projects/{project_id}/places/

Supported operations: - List all places for a project - Add a place
using `external_id` - Retrieve a single place - Update only `notes` and
`visited` - Delete a place (project must keep at least one place)

## Installation & Setup

### Requirements

-   Python 3.12+
-   pip

### Setup

``` bash
git clone https://github.com/diemonBil/travel-planner.git
cd travel-planner
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API available at:

    http://127.0.0.1:8000/api/

## Swagger

Interactive API documentation:

    http://127.0.0.1:8000/api/docs/

## Example: Create Project

``` json
{
  "name": "Paris Trip",
  "description": "Museums",
  "places": [42, 57, 68]
}
```

## Design Decisions

-   Explicit nested endpoints instead of writable nested serializers
-   Model-level validation
-   Clear REST boundaries
-   External API validation

## Future Improvements

-   Authentication
-   Caching
-   Tests